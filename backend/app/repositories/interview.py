from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import Interview


class InterviewRepository:
    """Data-access layer for :class:`Interview` entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, interview: Interview) -> Interview:
        self._session.add(interview)
        await self._session.flush()
        return interview

    async def get_by_id(self, interview_id: uuid.UUID) -> Interview | None:
        return await self._session.get(Interview, interview_id)

    async def get_by_application_id(
        self, application_id: uuid.UUID
    ) -> Interview | None:
        result = await self._session.execute(
            select(Interview).where(
                Interview.application_id == application_id
            )
        )
        return result.scalar_one_or_none()

    async def get_interview_ids_for_applications(
        self, application_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, uuid.UUID]:
        """Map application_id -> interview_id for the given applications."""
        if not application_ids:
            return {}
        result = await self._session.execute(
            select(Interview.id, Interview.application_id).where(
                Interview.application_id.in_(application_ids)
            )
        )
        return {row.application_id: row.id for row in result.all()}

    async def set_speech_metrics(
        self, interview: Interview, metrics: dict[str, Any]
    ) -> Interview:
        interview.speech_metrics = metrics
        self._session.add(interview)
        await self._session.flush()
        return interview

    async def set_video_metrics(
        self, interview: Interview, metrics: dict[str, Any]
    ) -> Interview:
        interview.video_metrics = metrics
        self._session.add(interview)
        await self._session.flush()
        return interview

    async def set_evaluation(
        self, interview: Interview, evaluation: dict[str, Any]
    ) -> Interview:
        interview.evaluation = evaluation
        self._session.add(interview)
        await self._session.flush()
        return interview
