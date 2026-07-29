from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileRead, ProfileUpdate
from app.services.profile import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileRead, summary="Get current user's profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Profile:
    return await ProfileService(session).get_for_user(current_user.id)


@router.put("", response_model=ProfileRead, summary="Update current user's profile")
async def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Profile:
    return await ProfileService(session).update_for_user(
        current_user.id, payload
    )
