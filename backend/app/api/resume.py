from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.resume import ResumeParsed, ResumeRead
from app.services.resume import ResumeService

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post(
    "/upload",
    response_model=ResumeRead,
    summary="Upload or replace the candidate's resume",
)
async def upload_resume(
    file: UploadFile,
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    session: AsyncSession = Depends(get_db),
) -> ResumeRead:
    data = await file.read()
    resume = await ResumeService(session).upload(
        current_user.id,
        file.filename or "resume",
        file.content_type or "application/octet-stream",
        data,
    )
    return ResumeRead.model_validate(resume)


@router.get(
    "",
    response_model=ResumeRead,
    summary="Get the candidate's resume metadata",
)
async def get_resume(
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    session: AsyncSession = Depends(get_db),
) -> ResumeRead:
    resume = await ResumeService(session).get_for_candidate(current_user.id)
    if resume is None:
        raise NotFoundError("No resume uploaded yet")
    return ResumeRead.model_validate(resume)


@router.get(
    "/download",
    summary="Download the candidate's resume file",
)
async def download_resume(
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    session: AsyncSession = Depends(get_db),
) -> Response:
    resume = await ResumeService(session).get_for_candidate(current_user.id)
    if resume is None or not resume.file_data:
        raise NotFoundError("No resume uploaded yet")
    return Response(
        resume.file_data,
        media_type=resume.content_type,
        headers={"Content-Disposition": f'attachment; filename="{resume.filename}"'},
    )


@router.delete(
    "",
    summary="Delete the candidate's resume",
)
async def delete_resume(
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    session: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    await ResumeService(session).delete_for_candidate(current_user.id)
    return {"message": "Resume deleted"}


@router.post(
    "/parse",
    response_model=ResumeParsed,
    summary="Parse the candidate's resume into text and profile fields",
)
async def parse_resume(
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    session: AsyncSession = Depends(get_db),
) -> ResumeParsed:
    result = await ResumeService(session).parse_into_profile(current_user.id)
    return ResumeParsed.model_validate(result)


@router.get(
    "/candidate/{user_id}",
    response_model=ResumeRead,
    summary="Get a candidate's resume metadata (recruiter)",
)
async def get_candidate_resume(
    user_id: uuid.UUID,
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
    session: AsyncSession = Depends(get_db),
) -> ResumeRead:
    resume = await ResumeService(session).get_for_candidate(user_id)
    if resume is None:
        raise NotFoundError("No resume uploaded yet")
    return ResumeRead.model_validate(resume)


@router.get(
    "/candidate/{user_id}/download",
    summary="Download a candidate's resume file (recruiter)",
)
async def download_candidate_resume(
    user_id: uuid.UUID,
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
    session: AsyncSession = Depends(get_db),
) -> Response:
    resume = await ResumeService(session).get_for_candidate(user_id)
    if resume is None or not resume.file_data:
        raise NotFoundError("No resume uploaded yet")
    return Response(
        resume.file_data,
        media_type=resume.content_type,
        headers={"Content-Disposition": f'attachment; filename="{resume.filename}"'},
    )
