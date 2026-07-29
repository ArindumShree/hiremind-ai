from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ProfileRead(BaseModel):
    """Public representation of a user profile."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    phone: str | None = None
    college: str | None = None
    company: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    bio: str | None = None
    profile_picture: str | None = None
    created_at: datetime
    updated_at: datetime


class ProfileUpdate(BaseModel):
    """Editable profile fields. All fields optional (partial update)."""

    phone: str | None = Field(default=None, max_length=32)
    college: str | None = Field(default=None, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    linkedin_url: HttpUrl | None = None
    github_url: HttpUrl | None = None
    bio: str | None = Field(default=None, max_length=2000)
    profile_picture: str | None = Field(default=None, max_length=512)
