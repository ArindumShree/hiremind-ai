from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.profile import Profile
from app.repositories.profile import ProfileRepository
from app.schemas.profile import ProfileUpdate


class ProfileService:
    """Business logic for reading and updating user profiles."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._profiles = ProfileRepository(session)

    async def get_for_user(self, user_id: uuid.UUID) -> Profile:
        profile = await self._profiles.get_by_user_id(user_id)
        if profile is None:
            raise NotFoundError("Profile not found")
        return profile

    async def update_for_user(
        self, user_id: uuid.UUID, payload: ProfileUpdate
    ) -> Profile:
        profile = await self.get_for_user(user_id)
        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            if field in {"linkedin_url", "github_url"} and value is not None:
                value = str(value)
            setattr(profile, field, value)
        await self._session.commit()
        await self._session.refresh(profile)
        return profile
