from __future__ import annotations

import os
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.errors import BadRequestError, NotFoundError
from app.models.application import Application
from app.models.enums import (
    ApplicationStatus,
    InterviewStatus,
)
from app.models.interview import Interview
from app.models.interview_media import InterviewMedia
from app.repositories.application import ApplicationRepository
from app.repositories.interview import InterviewRepository
from app.repositories.job import JobRepository
from app.repositories.profile import ProfileRepository
from app.services.job import JobService
from app.utils.time import utc_now

_GENERIC_QUESTIONS = [
    "Tell us about yourself and why you are interested in this role.",
    "Describe a challenging project you worked on and how you approached it.",
    "How do you prioritize work when handling multiple deadlines?",
    "What are your career goals for the next few years?",
    "Do you have any questions about the team or the role?",
]


class InterviewService:
    """Business logic for interview session lifecycle and answer capture."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._interviews = InterviewRepository(session)
        self._applications = ApplicationRepository(session)
        self._jobs = JobRepository(session)

    async def start_for_application(
        self, recruiter_id: uuid.UUID, application_id: uuid.UUID
    ) -> Interview:
        """Recruiter starts/schedules an interview for a shortlisted application."""
        application = await self._applications.get_by_id(application_id)
        if application is None:
            raise NotFoundError("Application not found")

        # Ownership: the application's job must belong to the recruiter.
        await JobService(self._session).get_owned(
            application.job_id, recruiter_id
        )

        if application.status not in (
            ApplicationStatus.SHORTLISTED,
            ApplicationStatus.APPLIED,
            ApplicationStatus.INTERVIEW_SCHEDULED,
        ):
            raise BadRequestError(
                "Interviews can only be started for active applications"
            )

        existing = await self._interviews.get_by_application_id(application_id)
        if existing is not None:
            raise BadRequestError(
                "An interview already exists for this application"
            )

        questions = await self._build_questions(application)

        interview = Interview(
            application_id=application_id,
            status=InterviewStatus.ACTIVE,
            questions_json=questions,
            started_at=utc_now(),
        )
        interview = await self._interviews.add(interview)

        application.status = ApplicationStatus.INTERVIEW_SCHEDULED
        self._session.add(application)

        await self._session.commit()
        await self._session.refresh(interview)
        return interview

    async def get_for_candidate(
        self, interview_id: uuid.UUID, candidate_id: uuid.UUID
    ) -> Interview:
        interview = await self._interviews.get_by_id(interview_id)
        if interview is None:
            raise NotFoundError("Interview not found")
        application = await self._applications.get_by_id(
            interview.application_id
        )
        if application is None or application.candidate_id != candidate_id:
            raise NotFoundError("Interview not found")
        return interview

    async def get_for_recruiter(
        self, interview_id: uuid.UUID, recruiter_id: uuid.UUID
    ) -> Interview:
        interview = await self._interviews.get_by_id(interview_id)
        if interview is None:
            raise NotFoundError("Interview not found")
        application = await self._applications.get_by_id(
            interview.application_id
        )
        if application is None:
            raise NotFoundError("Interview not found")
        # Ownership via the parent job.
        await JobService(self._session).get_owned(
            application.job_id, recruiter_id
        )
        return interview

    async def submit(
        self,
        interview_id: uuid.UUID,
        candidate_id: uuid.UUID,
        answers: list[dict],
    ) -> Interview:
        """Candidate submits captured answers (text and/or media references)."""
        interview = await self._interviews.get_by_id(interview_id)
        if interview is None:
            raise NotFoundError("Interview not found")

        application = await self._applications.get_by_id(
            interview.application_id
        )
        if application is None or application.candidate_id != candidate_id:
            raise NotFoundError("Interview not found")

        if interview.status == InterviewStatus.COMPLETED:
            raise BadRequestError("This interview has already been submitted")

        questions = interview.questions_json or []
        by_id: dict[str, dict] = {}
        for index, question in enumerate(questions):
            qid = question.get("id") or str(index)
            by_id[qid] = question

        captured: list[dict] = []
        for answer in answers:
            qid = answer.get("question_id", "")
            question = by_id.get(qid, {})
            captured.append(
                {
                    "question_id": qid,
                    "question_text": question.get("text"),
                    "text": answer.get("text"),
                    "media_path": answer.get("media_path"),
                    "media_type": answer.get("media_type"),
                }
            )

        interview.questions_json = captured
        interview.status = InterviewStatus.COMPLETED
        interview.submitted_at = utc_now()
        self._session.add(interview)

        if application.status != ApplicationStatus.INTERVIEW_COMPLETED:
            application.status = ApplicationStatus.INTERVIEW_COMPLETED
            self._session.add(application)

        await self._session.commit()
        await self._session.refresh(interview)
        return interview

    async def _resolve_for_analysis(
        self, interview_id: uuid.UUID, user
    ) -> Interview:
        """Fetch an interview enforcing candidate-owner or recruiter-owner access."""
        from app.models.enums import UserRole

        if user.role == UserRole.CANDIDATE:
            return await self.get_for_candidate(interview_id, user.id)
        if user.role == UserRole.RECRUITER:
            return await self.get_for_recruiter(interview_id, user.id)
        raise NotFoundError("Interview not found")

    def _first_media_path(
        self, interview: Interview, prefixes: tuple[str, ...]
    ) -> str | None:
        """Return the first stored media path matching one of the type prefixes."""
        for item in interview.questions_json or []:
            media_path = item.get("media_path")
            media_type = item.get("media_type") or ""
            if media_path and media_type.startswith(prefixes):
                return media_path
        # Fall back to any media path when the type is unknown.
        for item in interview.questions_json or []:
            media_path = item.get("media_path")
            if media_path:
                return media_path
        return None

    async def run_speech_analysis(
        self, interview_id: uuid.UUID, user
    ) -> Interview:
        interview = await self._resolve_for_analysis(interview_id, user)
        audio_ref = self._first_media_path(interview, ("audio", "video"))
        if not audio_ref:
            raise BadRequestError("No audio media found for this interview")
        audio_path = await self.resolve_media_ref(audio_ref)
        if not audio_path:
            raise BadRequestError("Audio media file is missing")

        from app.services.speech import SpeechAnalysisService

        metrics = SpeechAnalysisService().analyze(audio_path)
        await self._interviews.set_speech_metrics(
            interview, metrics.model_dump()
        )
        await self._session.commit()
        await self._session.refresh(interview)
        return interview

    async def run_video_analysis(
        self, interview_id: uuid.UUID, user
    ) -> Interview:
        interview = await self._resolve_for_analysis(interview_id, user)
        video_ref = self._first_media_path(interview, ("video",))
        if not video_ref:
            raise BadRequestError("No video media found for this interview")
        video_path = await self.resolve_media_ref(video_ref)
        if not video_path:
            raise BadRequestError("Video media file is missing")

        from app.services.video import VideoAnalysisService

        metrics = VideoAnalysisService().analyze(video_path)
        await self._interviews.set_video_metrics(
            interview, metrics.model_dump()
        )
        await self._session.commit()
        await self._session.refresh(interview)
        return interview

    async def run_evaluation(
        self, interview_id: uuid.UUID, user
    ) -> Interview:
        interview = await self._resolve_for_analysis(interview_id, user)

        from app.services.evaluation import EvaluationService

        evaluation = await EvaluationService().evaluate(interview)
        await self._interviews.set_evaluation(
            interview, evaluation.model_dump()
        )
        await self._session.commit()
        await self._session.refresh(interview)
        return interview

    async def _build_questions(
        self, application: Application
    ) -> list[dict]:
        """Build delivered questions, preferring AI generation when available."""
        job = await self._jobs.get_by_id(application.job_id)
        if job is None or job.is_deleted:
            raise NotFoundError("Job not found")

        profile = await ProfileRepository(self._session).get_by_user_id(
            application.candidate_id
        )

        try:
            from app.services.question import QuestionService

            if (
                settings.NVIDIA_API_KEY
                and settings.NVIDIA_API_KEY.strip()
            ):
                generated = await QuestionService(self._session).generate(
                    job, profile
                )
                if generated:
                    return [
                        {"id": str(i), **item}
                        for i, item in enumerate(generated)
                    ]
        except Exception:  # pragma: no cover - offline / API unavailable
            pass

        return [
            {"id": str(i), "text": text, "category": "general"}
            for i, text in enumerate(_GENERIC_QUESTIONS)
        ]

    async def save_media(
        self, interview_id: uuid.UUID, filename: str, content_type: str, data: bytes
    ) -> str:
        """Persist an uploaded answer media file into the database.

        Returns a ``db://`` reference that resolves to the stored bytes.
        """
        media = InterviewMedia(
            interview_id=interview_id,
            filename=filename,
            content_type=content_type or "application/octet-stream",
            size_bytes=len(data),
            file_data=data,
        )
        self._session.add(media)
        await self._session.flush()
        return f"db://interviews/{interview_id}/{media.id}"

    async def resolve_media_ref(self, ref: str) -> str | None:
        """Return the file path for a stored media reference.

        ``db://`` refs need to be materialized to a temp file before they can be
        consumed by file-based libraries (Whisper, OpenCV). Local paths are
        returned unchanged.
        """
        if not ref.startswith("db://"):
            return ref if os.path.exists(ref) else None
        media_id = ref.rsplit("/", 1)[-1]
        from sqlalchemy import select

        result = await self._session.execute(
            select(InterviewMedia).where(InterviewMedia.id == media_id)
        )
        media = result.scalar_one_or_none()
        if media is None or not media.file_data:
            return None
        extension = os.path.splitext(media.filename)[1].lower() or ".bin"
        temp_path = os.path.join(
            "/tmp", "interview_media", str(media.id) + extension
        )
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        if not os.path.exists(temp_path):
            with open(temp_path, "wb") as handle:
                handle.write(media.file_data)
        return temp_path

    async def get_media_bytes(
        self, ref: str
    ) -> tuple[bytes | None, str, str]:
        """Return (bytes, filename, content_type) for a stored media reference."""
        if ref.startswith("db://"):
            media_id = ref.rsplit("/", 1)[-1]
            from sqlalchemy import select

            result = await self._session.execute(
                select(InterviewMedia).where(InterviewMedia.id == media_id)
            )
            media = result.scalar_one_or_none()
            if media is None:
                return None, "answer", "application/octet-stream"
            return (
                media.file_data,
                media.filename,
                media.content_type,
            )
        return None, "answer", "application/octet-stream"
