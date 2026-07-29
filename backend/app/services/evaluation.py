from __future__ import annotations

from app.config.settings import settings
from app.models.interview import Interview
from app.schemas.analysis import Evaluation, EvaluationDimension

_WEIGHTS = {
    "communication": 0.35,
    "engagement": 0.30,
    "content": 0.35,
}


def _answer_content_score(interview: Interview) -> float:
    """Heuristic 0-100 score for the completeness of textual answers."""
    questions = interview.questions_json or []
    if not questions:
        return 0.0
    answered = [q for q in questions if (q.get("text") or "").strip()]
    if not answered:
        return 0.0
    completeness = len(answered) / max(len(questions), 1)
    avg_len = sum(len(q.get("text") or "") for q in answered) / len(answered)
    depth = min(1.0, avg_len / 300.0)
    return round((completeness * 0.6 + depth * 0.4) * 100.0, 2)


def compute_evaluation(interview: Interview) -> Evaluation:
    """Combine speech + video + answers into a weighted evaluation (pure)."""
    speech = interview.speech_metrics or {}
    video = interview.video_metrics or {}

    communication = round(
        (
            float(speech.get("fluency_score", 0.0)) * 0.5
            + float(speech.get("confidence_score", 0.0)) * 0.5
        )
        * 100.0,
        2,
    )
    engagement = round(
        (
            float(video.get("engagement_score", 0.0)) * 0.6
            + float(video.get("eye_contact_score", 0.0)) * 0.4
        )
        * 100.0,
        2,
    )
    content = _answer_content_score(interview)

    dimensions = [
        EvaluationDimension(
            name="communication",
            score=communication,
            weight=_WEIGHTS["communication"],
        ),
        EvaluationDimension(
            name="engagement",
            score=engagement,
            weight=_WEIGHTS["engagement"],
        ),
        EvaluationDimension(
            name="content",
            score=content,
            weight=_WEIGHTS["content"],
        ),
    ]
    overall = round(sum(d.score * d.weight for d in dimensions), 2)

    summary = (
        f"Overall score {overall}/100. "
        f"Communication {communication}, engagement {engagement}, "
        f"content {content}."
    )

    return Evaluation(
        overall_score=overall,
        dimensions=dimensions,
        summary=summary,
        ai_feedback=None,
    )


class EvaluationService:
    """Produce a candidate evaluation, optionally enriched via Gemini."""

    async def evaluate(self, interview: Interview) -> Evaluation:
        """Compute the weighted evaluation and add Gemini feedback if possible."""
        evaluation = compute_evaluation(interview)
        feedback = await self._maybe_gemini_feedback(interview, evaluation)
        if feedback:
            evaluation.ai_feedback = feedback
        return evaluation

    async def _maybe_gemini_feedback(
        self, interview: Interview, evaluation: Evaluation
    ) -> str | None:
        """Call NVIDIA's API for a natural-language summary; degrade gracefully."""
        if not settings.NVIDIA_API_KEY or not settings.NVIDIA_API_KEY.strip():
            return None
        try:
            import httpx  # noqa: PLC0415

            dims = ", ".join(
                f"{d.name}={d.score}" for d in evaluation.dimensions
            )
            answers = [
                (q.get("text") or "")
                for q in (interview.questions_json or [])
                if (q.get("text") or "").strip()
            ]
            prompt = (
                "You are an expert interviewer. Given these scores and "
                "candidate answers, write a concise 3-4 sentence hiring "
                f"feedback summary.\n\nScores: overall="
                f"{evaluation.overall_score}, {dims}.\n\n"
                f"Answers: {' | '.join(answers)[:2000]}"
            )
            url = f"{settings.NVIDIA_BASE_URL.rstrip('/')}/chat/completions"
            headers = {
                "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": settings.NVIDIA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 512,
            }
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                return None
            data = resp.json()
            text = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                or ""
            )
            return text.strip() or None
        except Exception:  # pragma: no cover - offline / API unavailable
            return None
