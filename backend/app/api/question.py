from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.job import JobRepository
from app.repositories.profile import ProfileRepository
from app.schemas.question import (
    QuestionGenerateRequest,
    QuestionList,
)
from app.services.question import QuestionService

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post(
    "/generate",
    response_model=QuestionList,
    summary="Generate role-based interview questions for a job (candidate only)",
)
async def generate_questions(
    payload: QuestionGenerateRequest,
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    session: AsyncSession = Depends(get_db),
) -> QuestionList:
    jobs = JobRepository(session)
    job = await jobs.get_by_id(payload.job_id)
    if job is None or job.is_deleted:
        raise NotFoundError("Job not found")

    profile = None
    if payload.profile_id is not None:
        profile = await ProfileRepository(session).get_by_user_id(payload.profile_id)

    raw = await QuestionService(session).generate(job, profile)
    return QuestionList(
        questions=[{"text": item["text"], "category": item["category"]} for item in raw]
    )
