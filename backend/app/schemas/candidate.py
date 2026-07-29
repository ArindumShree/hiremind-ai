from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ApplicationStatus, InterviewStatus


class CandidateSummary(BaseModel):
    """A compact, recruiter-facing view of a candidate for one of their jobs."""

    model_config = ConfigDict(from_attributes=True)

    application_id: uuid.UUID
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    job_title: str | None = None
    full_name: str
    email: str
    status: ApplicationStatus
    applied_at: datetime
    skills: list[str] = Field(default_factory=list)
    experience_years: int | None = None
    college: str | None = None
    interview_status: InterviewStatus | None = None
    interview_score: float | None = None
    evaluation_summary: str | None = None
    evaluation: dict[str, Any] | None = None


class CandidateDetail(CandidateSummary):
    """Full detail view including resume profile, interview and evaluation."""

    cover_letter: str | None = None
    profile: dict[str, Any] | None = None
    interview_questions: list[dict[str, Any]] | None = None
    parsed_fields: dict[str, Any] | None = None


class CandidateComparison(BaseModel):
    """Side-by-side comparison of two or more candidates."""

    candidates: list[CandidateDetail]
    generated_at: datetime


class CompareRequest(BaseModel):
    """Body for the compare endpoint: application (or candidate) ids."""

    application_ids: list[uuid.UUID] = Field(
        default_factory=list, description="Application ids to compare"
    )


class CandidateReport(BaseModel):
    """Portable JSON report for a single candidate."""

    candidate_id: uuid.UUID
    candidate_name: str
    candidate_email: str
    job_title: str | None = None
    application_status: ApplicationStatus
    applied_at: datetime
    skills: list[str] = Field(default_factory=list)
    experience_years: int | None = None
    college: str | None = None
    profile: dict[str, Any] | None = None
    interview_status: InterviewStatus | None = None
    interview_score: float | None = None
    evaluation_summary: str | None = None
    interview_questions: list[dict[str, Any]] | None = None
    generated_at: datetime
