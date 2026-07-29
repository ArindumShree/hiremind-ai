from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AnswerItem(BaseModel):
    """A single captured answer, keyed to a delivered question."""

    question_id: str = Field(min_length=1)
    text: str | None = Field(default=None, max_length=20000)
    # For audio/video answers, the stored media reference path.
    media_path: str | None = Field(default=None, max_length=1024)
    media_type: str | None = Field(default=None, max_length=127)


class InterviewCreate(BaseModel):
    """Payload to start an interview for an application."""

    application_id: uuid.UUID


class InterviewSubmit(BaseModel):
    """Payload with captured answers for an interview."""

    answers: list[AnswerItem] = Field(default_factory=list)


class InterviewRead(BaseModel):
    """Public representation of an interview session."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    status: str
    questions: list[dict[str, Any]] | None = None
    started_at: datetime | None = None
    submitted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("status", mode="before")
    @classmethod
    def _status_to_str(cls, value: Any) -> Any:
        if hasattr(value, "value"):
            return value.value
        return value

    @model_validator(mode="before")
    @classmethod
    def _populate_questions(cls, data: Any) -> Any:
        # When built from an ORM object, map questions_json -> questions.
        if hasattr(data, "questions_json"):
            object.__setattr__(data, "questions", data.questions_json)
        elif isinstance(data, dict) and data.get("questions") is None and "questions_json" in data:
            data["questions"] = data["questions_json"]
        return data

