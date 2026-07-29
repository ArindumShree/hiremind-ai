from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeRead(BaseModel):
    """Metadata for a candidate's uploaded resume (no file bytes)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    candidate_id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    created_at: datetime


class ResumeParsed(BaseModel):
    """Result of parsing a candidate's resume into text and profile fields."""

    parsed_text: str
    parsed_fields: dict[str, object | None]
