from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ApplicationStatus
from app.schemas.user import UserRead


class ApplicationCreate(BaseModel):
    """Payload for a candidate applying to a job."""

    cover_letter: str | None = Field(default=None, max_length=10000)


class ApplicationStatusUpdate(BaseModel):
    """Payload for a recruiter updating an application's status."""

    status: ApplicationStatus


class ApplicationRead(BaseModel):
    """Public representation of an application."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    status: ApplicationStatus
    cover_letter: str | None = None
    applied_at: datetime
    updated_at: datetime
    candidate: UserRead | None = None
    interview_id: uuid.UUID | None = None
