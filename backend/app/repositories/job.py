from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import JobStatus
from app.models.job import Job
from app.utils.time import utc_now


class JobRepository:
    """Data-access layer for :class:`Job` entities (soft-delete aware)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, job: Job) -> Job:
        self._session.add(job)
        await self._session.flush()
        return job

    async def get_by_id(self, job_id: uuid.UUID) -> Job | None:
        return await self._session.get(Job, job_id)

    async def get_owned_by_id(
        self, job_id: uuid.UUID, recruiter_id: uuid.UUID
    ) -> Job | None:
        """Return a non-deleted job only if owned by ``recruiter_id``."""
        result = await self._session.execute(
            select(Job).where(
                Job.id == job_id,
                Job.posted_by == recruiter_id,
                Job.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def exists(self, job_id: uuid.UUID) -> bool:
        result = await self._session.execute(
            select(Job.id).where(
                Job.id == job_id, Job.is_deleted.is_(False)
            )
        )
        return result.first() is not None

    async def list_by_recruiter(
        self, recruiter_id: uuid.UUID
    ) -> list[Job]:
        result = await self._session.execute(
            select(Job)
            .where(Job.posted_by == recruiter_id, Job.is_deleted.is_(False))
            .order_by(Job.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_published(
        self,
        *,
        search: str | None = None,
        location: str | None = None,
        employment_type: Any | None = None,
        status: JobStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Job], int]:
        """Return a page of visible jobs (published by default) + total count."""
        filters = [Job.is_deleted.is_(False)]
        if status is not None:
            filters.append(Job.status == status)
        else:
            filters.append(Job.status == JobStatus.PUBLISHED)
        if search:
            like = f"%{search.strip()}%"
            filters.append(Job.title.ilike(like) | Job.company_name.ilike(like))
        if location:
            filters.append(Job.location.ilike(f"%{location.strip()}%"))
        if employment_type is not None:
            filters.append(Job.employment_type == employment_type)

        total_result = await self._session.execute(
            select(Job.id).where(*filters)
        )
        total = len(total_result.all())

        result = await self._session.execute(
            select(Job)
            .where(*filters)
            .order_by(Job.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def soft_delete(self, job: Job) -> None:
        job.is_deleted = True
        job.deleted_at = utc_now()
        self._session.add(job)
        await self._session.flush()
