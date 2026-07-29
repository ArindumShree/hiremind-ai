from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import UserRole
from app.schemas.profile import ProfileRead


class UserRead(BaseModel):
    """Public representation of a user. Never exposes the password hash."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserWithProfile(UserRead):
    """User representation including the associated profile."""

    profile: ProfileRead | None = None
