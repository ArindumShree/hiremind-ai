from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """Data-access layer for :class:`RefreshToken` entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self, *, jti: str, user_id: uuid.UUID, expires_at: datetime
    ) -> RefreshToken:
        token = RefreshToken(jti=jti, user_id=user_id, expires_at=expires_at)
        self._session.add(token)
        await self._session.flush()
        return token

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self._session.execute(
            select(RefreshToken).where(RefreshToken.jti == jti)
        )
        return result.scalar_one_or_none()

    async def revoke(self, jti: str) -> None:
        await self._session.execute(
            update(RefreshToken)
            .where(RefreshToken.jti == jti)
            .values(revoked=True)
        )

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        await self._session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(revoked=True)
        )
