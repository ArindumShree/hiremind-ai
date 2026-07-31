from __future__ import annotations

import re
from typing import Any

import httpx

from app.config.settings import settings
from app.core.errors import BadRequestError
from app.models.job import Job
from app.models.profile import Profile

_ENGINEER_KEYWORDS = (
    "engineer",
    "developer",
    "programmer",
    "software",
    "backend",
    "frontend",
    "full stack",
    "fullstack",
    "devops",
    "sre",
)
_DESIGNER_KEYWORDS = (
    "designer",
    "ux",
    "ui",
    "product design",
    "graphic",
    "visual",
)


def _role_category(title: str) -> str:
    lowered = title.lower()
    if any(keyword in lowered for keyword in _ENGINEER_KEYWORDS):
        return "engineer"
    if any(keyword in lowered for keyword in _DESIGNER_KEYWORDS):
        return "designer"
    return "generic"


def build_prompt(job: Job, profile: Profile | None = None) -> str:
    """Build a role-aware prompt for the Gemini model from a job + profile."""
    category = _role_category(job.title)

    base = (
        "You are an expert technical interviewer. "
        "Generate a list of interview questions tailored to the role below. "
        "Return each question on its own line, prefixed with a number "
        "and a period (for example '1. ...'). Do not include any commentary, "
        "headers, or blank lines."
    )

    role_block = (
        f"\n\nRole: {job.title}"
        f"\nCompany: {job.company_name or 'N/A'}"
        f"\nEmployment type: {job.employment_type.value if job.employment_type else 'N/A'}"
        f"\nExperience required: {job.experience_required or 'N/A'}"
        f"\nDescription: {job.description or 'N/A'}"
        f"\nRequirements: {job.requirements or 'N/A'}"
        f"\nResponsibilities: {job.responsibilities or 'N/A'}"
        f"\nSkills required: {job.skills_required or 'N/A'}"
    )

    if category == "engineer":
        focus = (
            "\n\nFocus on: system design, coding proficiency, debugging, and "
            "collaboration in a software engineering context. Mix behavioral "
            "and technical questions."
        )
    elif category == "designer":
        focus = (
            "\n\nFocus on: design thinking, portfolio critique, user research, "
            "and collaboration with engineering. Mix behavioral and craft "
            "questions."
        )
    else:
        focus = (
            "\n\nFocus on: role-relevant competencies, past experience, and "
            "behavioral questions that reveal fit and motivation."
        )

    profile_block = ""
    if profile is not None:
        profile_block = (
            f"\n\nCandidate context (use to tailor and deepen questions): "
            f"college={profile.college or 'N/A'}, "
            f"phone on file={bool(profile.phone)}, "
            f"links: github={profile.github_url or 'N/A'}, "
            f"linkedin={profile.linkedin_url or 'N/A'}, "
            f"bio={profile.bio or 'N/A'}"
        )

    return base + role_block + focus + profile_block


def parse_questions(raw: str) -> list[dict[str, Any]]:
    """Parse a model response into a clean list of {text, category} dicts."""
    questions: list[dict[str, Any]] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = re.match(r"^\d+[\).]\s*(.*)$", stripped)
        if match:
            text = match.group(1).strip()
        else:
            text = stripped
        if not text:
            continue
        questions.append({"text": text, "category": None})
    return questions


class QuestionService:
    """Generate role-based interview questions via NVIDIA's API."""

    def __init__(self, session: Any | None = None) -> None:
        self._session = session

    async def generate(
        self, job: Job, profile: Profile | None = None
    ) -> list[dict[str, Any]]:
        """Build a role-based prompt and return generated questions."""
        if not settings.NVIDIA_API_KEY or not settings.NVIDIA_API_KEY.strip():
            raise BadRequestError("NVIDIA API key not configured")

        prompt = build_prompt(job, profile)
        url = f"{settings.NVIDIA_BASE_URL.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.NVIDIA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        async with httpx.AsyncClient(timeout=25.0) as client:
            try:
                resp = await client.post(url, json=payload, headers=headers)
            except httpx.HTTPError as exc:
                raise BadRequestError(f"NVIDIA API request failed: {exc}") from exc

            if resp.status_code != 200:
                detail = resp.text[:300]
                raise BadRequestError(
                    f"NVIDIA API error {resp.status_code}: {detail}"
                )

            data = resp.json()

        raw = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            or ""
        )
        return parse_questions(raw)
