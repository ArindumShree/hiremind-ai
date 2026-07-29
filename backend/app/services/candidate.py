from __future__ import annotations

import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.application import Application
from app.models.enums import ApplicationStatus
from app.repositories.candidate import CandidateRepository
from app.utils.time import utc_now

_SKILL_STOPWORDS = {
    "and", "with", "the", "for", "you", "our", "are", "who", "have", "will",
}


def _extract_experience_years(text: str | None) -> int | None:
    if not text:
        return None
    match = re.search(r"(\d{1,2})\+?\s*(?:years?|yrs?)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def _derive_skills(text: str | None, skills_required: str | None) -> list[str]:
    skills: list[str] = []
    if skills_required:
        for raw in re.split(r"[,\n;]|\\n", skills_required):
            token = raw.strip()
            if token and token.lower() not in _SKILL_STOPWORDS:
                skills.append(token)
    if text and not skills:
        # Fall back to capitalized technical-looking words.
        for token in re.findall(r"\b([A-Z][A-Za-z+#]{2,})\b", text):
            if token.lower() not in _SKILL_STOPWORDS and token not in skills:
                skills.append(token)
    # De-duplicate while preserving order.
    seen: set[str] = set()
    unique: list[str] = []
    for skill in skills:
        key = skill.lower()
        if key not in seen:
            seen.add(key)
            unique.append(skill)
    return unique


def _interview_score(interview) -> float | None:
    if interview is None or interview.questions_json is None:
        return None
    answered = [q for q in interview.questions_json if q.get("text")]
    if not answered:
        return None
    # Heuristic completeness score: fraction of questions with a text answer.
    return round(len(answered) / max(len(interview.questions_json), 1), 2)


def _evaluation_summary(application: Application) -> str | None:
    interview = application.interview
    if interview is None:
        return None
    # Prefer a stored AI evaluation summary where available.
    evaluation = getattr(interview, "evaluation", None)
    if evaluation:
        return evaluation.get("ai_feedback") or evaluation.get("summary")
    if not interview.questions_json:
        return None
    answers = [
        q.get("text")
        for q in interview.questions_json
        if q.get("text")
    ]
    if not answers:
        return None
    joined = " ".join(answers)
    return joined[:1000]


class CandidateService:
    """Business logic for recruiters reviewing candidates across their jobs."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._candidates = CandidateRepository(session)

    async def list_for_recruiter(
        self,
        recruiter_id: uuid.UUID,
        *,
        job_id: uuid.UUID | None = None,
        status: ApplicationStatus | None = None,
        search: str | None = None,
    ) -> list[dict]:
        applications = await self._candidates.list_for_recruiter(
            recruiter_id, job_id=job_id, status=status, search=search
        )
        return [self._summarize(app) for app in applications]

    async def get_detail(
        self, application_id: uuid.UUID, recruiter_id: uuid.UUID
    ) -> dict:
        application = await self._candidates.get_for_recruiter(
            application_id, recruiter_id
        )
        if application is None:
            raise NotFoundError("Candidate application not found")
        return self._detail(application)

    async def compare(
        self,
        recruiter_id: uuid.UUID,
        application_ids: list[uuid.UUID],
    ) -> dict:
        applications = await self._candidates.list_by_ids_for_recruiter(
            recruiter_id, application_ids
        )
        if len(applications) != len(application_ids):
            raise NotFoundError(
                "One or more applications were not found for your jobs"
            )
        details = [self._detail(app) for app in applications]
        return {
            "candidates": details,
            "generated_at": utc_now(),
        }

    async def build_report(
        self, application_id: uuid.UUID, recruiter_id: uuid.UUID
    ) -> dict:
        application = await self._candidates.get_for_recruiter(
            application_id, recruiter_id
        )
        if application is None:
            raise NotFoundError("Candidate application not found")
        detail = self._detail(application)
        return {
            "candidate_id": detail["candidate_id"],
            "candidate_name": detail["full_name"],
            "candidate_email": detail["email"],
            "job_title": detail["job_title"],
            "application_status": detail["status"],
            "applied_at": detail["applied_at"],
            "skills": detail["skills"],
            "experience_years": detail["experience_years"],
            "college": detail["college"],
            "profile": detail["profile"],
            "interview_status": detail["interview_status"],
            "interview_score": detail["interview_score"],
            "evaluation_summary": detail["evaluation_summary"],
            "interview_questions": detail["interview_questions"],
            "generated_at": utc_now(),
        }

    def _summarize(self, application: Application) -> dict:
        candidate = application.candidate
        job = application.job
        bio = candidate.profile.bio if candidate.profile else None
        job_skills = job.skills_required if job else None
        return {
            "application_id": application.id,
            "candidate_id": candidate.id,
            "job_id": application.job_id,
            "job_title": job.title if job else None,
            "full_name": candidate.full_name,
            "email": candidate.email,
            "status": application.status,
            "applied_at": application.applied_at,
            "skills": _derive_skills(bio, job_skills),
            "experience_years": _extract_experience_years(bio),
            "college": (
                candidate.profile.college if candidate.profile else None
            ),
            "interview_status": (
                application.interview.status if application.interview else None
            ),
            "interview_score": _interview_score(application.interview),
            "evaluation_summary": _evaluation_summary(application),
            "evaluation": (
                getattr(application.interview, "evaluation", None)
                if application.interview
                else None
            ),
        }

    def _detail(self, application: Application) -> dict:
        summary = self._summarize(application)
        candidate = application.candidate
        profile = (
            {
                "phone": candidate.profile.phone,
                "college": candidate.profile.college,
                "company": candidate.profile.company,
                "linkedin_url": candidate.profile.linkedin_url,
                "github_url": candidate.profile.github_url,
                "bio": candidate.profile.bio,
            }
            if candidate.profile
            else None
        )
        parsed_fields = None
        if candidate.profile and candidate.profile.bio:
            from app.services.resume import parse_profile_fields

            parsed_fields = parse_profile_fields(candidate.profile.bio)

        interview_questions = (
            application.interview.questions_json
            if application.interview
            else None
        )
        return {
            **summary,
            "cover_letter": application.cover_letter,
            "profile": profile,
            "interview_questions": interview_questions,
            "parsed_fields": parsed_fields,
        }
