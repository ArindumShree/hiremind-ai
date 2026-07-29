from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field


class Question(BaseModel):
    """A single generated interview question."""

    text: str = Field(min_length=1, max_length=2000)
    category: str | None = Field(default=None, max_length=255)


class QuestionList(BaseModel):
    """A list of generated interview questions."""

    questions: list[Question]


class QuestionGenerateRequest(BaseModel):
    """Request payload to generate questions for a job."""

    job_id: uuid.UUID
    profile_id: uuid.UUID | None = Field(default=None)


class QuestionGenerateResponse(BaseModel):
    """Response payload for generated questions."""

    model_config = ConfigDict(from_attributes=True)

    questions: list[Question]
