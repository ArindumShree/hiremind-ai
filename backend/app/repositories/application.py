from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application


class ApplicationRepository:
    """Data-access layer for :class:`Application` entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, application: Application) -> Application:
        self._session.add(application)
        await self._session.flush()
        return application

    async def exists_for_user_and_job(
        self, candidate_id: uuid.UUID, job_id: uuid.UUID
    ) -> bool:
        result = await self._session.execute(
            select(Application.id).where(
                Application.candidate_id == candidate_id,
                Application.job_id == job_id,
            )
        )
        return result.first() is not None

    async def get_by_id(self, application_id: uuid.UUID) -> Application | None:
        return await self._session.get(Application, application_id)

    async def list_by_candidate(
        self, candidate_id: uuid.UUID
    ) -> list[Application]:
        result = await self._session.execute(
            select(Application)
            .where(Application.candidate_id == candidate_id)
            .order_by(Application.applied_at.desc())
        )
        return list(result.scalars().all())

    async def list_by_job(self, job_id: uuid.UUID) -> list[Application]:
        result = await self._session.execute(
            select(Application)
            .where(Application.job_id == job_id)
            .order_by(Application.applied_at.desc())
        )
        return list(result.scalars().all())
