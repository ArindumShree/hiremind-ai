from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application
from app.models.job import Job
from app.models.user import User


class CandidateRepository:
    """Data-access layer for recruiter-facing candidate (application) queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _base_options(self):
        return (
            selectinload(Application.candidate).selectinload(User.profile),
            selectinload(Application.candidate).selectinload(User.resume),
            selectinload(Application.job),
            selectinload(Application.interview),
        )

    async def list_for_recruiter(
        self,
        recruiter_id: uuid.UUID,
        *,
        job_id: uuid.UUID | None = None,
        status: object | None = None,
        search: str | None = None,
    ) -> list[Application]:
        filters = [
            Job.posted_by == recruiter_id,
            Job.is_deleted.is_(False),
        ]
        if job_id is not None:
            filters.append(Application.job_id == job_id)
        if status is not None:
            filters.append(Application.status == status)
        if search:
            like = f"%{search.strip()}%"
            filters.append(
                User.full_name.ilike(like) | User.email.ilike(like)
            )

        result = await self._session.execute(
            select(Application)
            .join(Job, Application.job_id == Job.id)
            .join(User, Application.candidate_id == User.id)
            .where(*filters)
            .options(*self._base_options())
            .order_by(Application.applied_at.desc())
        )
        return list(result.scalars().all())

    async def list_by_ids_for_recruiter(
        self,
        recruiter_id: uuid.UUID,
        application_ids: list[uuid.UUID],
    ) -> list[Application]:
        if not application_ids:
            return []

        result = await self._session.execute(
            select(Application)
            .join(Job, Application.job_id == Job.id)
            .where(
                Application.id.in_(application_ids),
                Job.posted_by == recruiter_id,
                Job.is_deleted.is_(False),
            )
            .options(*self._base_options())
        )
        return list(result.scalars().all())

    async def get_for_recruiter(
        self,
        application_id: uuid.UUID,
        recruiter_id: uuid.UUID,
    ) -> Application | None:
        result = await self._session.execute(
            select(Application)
            .join(Job, Application.job_id == Job.id)
            .where(
                Application.id == application_id,
                Job.posted_by == recruiter_id,
                Job.is_deleted.is_(False),
            )
            .options(*self._base_options())
        )
        return result.scalar_one_or_none()
