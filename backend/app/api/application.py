from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, parse_job_id, require_role
from app.core.database import get_db
from app.models.application import Application
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationStatusUpdate,
)
from app.services.job import ApplicationService

router = APIRouter(prefix="/jobs", tags=["applications"])


@router.post(
    "/{job_id}/apply",
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.CANDIDATE))],
    summary="Apply to a job (candidate only)",
)
async def apply_to_job(
    payload: ApplicationCreate,
    job_id: uuid.UUID = Depends(parse_job_id),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Application:
    return await ApplicationService(session).apply(
        current_user.id, job_id, payload.cover_letter
    )


@router.get(
    "/{job_id}/applications",
    response_model=list[ApplicationRead],
    dependencies=[Depends(require_role(UserRole.RECRUITER))],
    summary="List applicants for a job (owner only)",
)
async def list_applicants(
    job_id: uuid.UUID = Depends(parse_job_id),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[ApplicationRead]:
    return await ApplicationService(session).list_for_job(job_id, current_user.id)


candidate_router = APIRouter(prefix="/applications", tags=["applications"])


@candidate_router.get(
    "/my",
    response_model=list[ApplicationRead],
    dependencies=[Depends(require_role(UserRole.CANDIDATE))],
    summary="List the current candidate's applications",
)
async def list_my_applications(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[ApplicationRead]:
    return await ApplicationService(session).list_mine(current_user.id)


@candidate_router.patch(
    "/{application_id}/status",
    response_model=ApplicationRead,
    dependencies=[Depends(require_role(UserRole.RECRUITER))],
    summary="Update an application's status (job owner only)",
)
async def update_application_status(
    payload: ApplicationStatusUpdate,
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Application:
    return await ApplicationService(session).update_status(
        application_id, current_user.id, payload.status
    )
