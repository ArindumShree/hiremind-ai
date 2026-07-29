from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, parse_job_id, require_role
from app.core.database import get_db
from app.models.enums import EmploymentType, JobStatus, UserRole
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobRead, JobUpdate
from app.schemas.pagination import PaginatedResponse
from app.services.job import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post(
    "",
    response_model=JobRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.RECRUITER))],
    summary="Create a job (recruiter only)",
)
async def create_job(
    payload: JobCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Job:
    return await JobService(session).create(current_user.id, payload)


@router.get(
    "/my",
    response_model=list[JobRead],
    dependencies=[Depends(require_role(UserRole.RECRUITER))],
    summary="List jobs created by the current recruiter",
)
async def list_my_jobs(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[Job]:
    return await JobService(session).list_mine(current_user.id)


@router.get(
    "", response_model=PaginatedResponse[JobRead], summary="Browse published jobs"
)
async def browse_jobs(
    search: str | None = Query(default=None, description="Match title or company"),
    location: str | None = Query(default=None),
    employment_type: EmploymentType | None = Query(default=None),
    status: JobStatus | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    items, meta = await JobService(session).browse(
        search=search,
        location=location,
        employment_type=employment_type,
        status=status,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(items=items, meta=meta)


@router.get("/{job_id}", response_model=JobRead, summary="Get a job by id")
async def get_job(
    job_id: uuid.UUID = Depends(parse_job_id),
    session: AsyncSession = Depends(get_db),
) -> Job:
    job = await JobService(session)._jobs.get_by_id(job_id)
    if job is None or job.is_deleted:
        from app.core.errors import NotFoundError

        raise NotFoundError("Job not found")
    return job


@router.put(
    "/{job_id}",
    response_model=JobRead,
    dependencies=[Depends(require_role(UserRole.RECRUITER))],
    summary="Update a job (owner only)",
)
async def update_job(
    payload: JobUpdate,
    job_id: uuid.UUID = Depends(parse_job_id),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Job:
    return await JobService(session).update(job_id, current_user.id, payload)


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(UserRole.RECRUITER))],
    summary="Delete a job (owner only, soft delete)",
)
async def delete_job(
    job_id: uuid.UUID = Depends(parse_job_id),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    await JobService(session).delete(job_id, current_user.id)


@router.patch(
    "/{job_id}/publish",
    response_model=JobRead,
    dependencies=[Depends(require_role(UserRole.RECRUITER))],
    summary="Publish a job (owner only)",
)
async def publish_job(
    job_id: uuid.UUID = Depends(parse_job_id),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Job:
    return await JobService(session).publish(job_id, current_user.id)


@router.patch(
    "/{job_id}/close",
    response_model=JobRead,
    dependencies=[Depends(require_role(UserRole.RECRUITER))],
    summary="Close a job (owner only)",
)
async def close_job(
    job_id: uuid.UUID = Depends(parse_job_id),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Job:
    return await JobService(session).close(job_id, current_user.id)
