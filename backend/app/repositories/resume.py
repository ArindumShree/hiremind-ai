from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume


class ResumeRepository:
    """Data-access layer for :class:`Resume` entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_candidate_id(
        self, candidate_id: uuid.UUID
    ) -> Resume | None:
        result = await self._session.execute(
            select(Resume).where(Resume.candidate_id == candidate_id)
        )
        return result.scalar_one_or_none()

    async def add(self, resume: Resume) -> Resume:
        self._session.add(resume)
        await self._session.flush()
        return resume

    async def delete_by_candidate_id(self, candidate_id: uuid.UUID) -> None:
        await self._session.execute(
            delete(Resume).where(Resume.candidate_id == candidate_id)
        )
