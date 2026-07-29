from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EmploymentType, JobStatus


class JobBase(BaseModel):
    """Shared writable fields for job postings."""

    title: str = Field(min_length=1, max_length=255)
    company_name: str = Field(min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    employment_type: EmploymentType | None = None
    experience_required: str | None = Field(default=None, max_length=255)
    salary_range: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    requirements: str | None = Field(default=None, max_length=10000)
    responsibilities: str | None = Field(default=None, max_length=10000)
    skills_required: str | None = Field(default=None, max_length=5000)


class JobCreate(JobBase):
    """Payload for creating a new job."""


class JobUpdate(BaseModel):
    """Editable job fields. All fields optional (partial update)."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    company_name: str | None = Field(default=None, min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    employment_type: EmploymentType | None = None
    experience_required: str | None = Field(default=None, max_length=255)
    salary_range: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    requirements: str | None = Field(default=None, max_length=10000)
    responsibilities: str | None = Field(default=None, max_length=10000)
    skills_required: str | None = Field(default=None, max_length=5000)


class JobRead(BaseModel):
    """Public representation of a job posting."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    company_name: str
    location: str | None = None
    employment_type: EmploymentType | None = None
    experience_required: str | None = None
    salary_range: str | None = None
    description: str | None = None
    requirements: str | None = None
    responsibilities: str | None = None
    skills_required: str | None = None
    status: JobStatus
    posted_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class JobListParams(BaseModel):
    """Query parameters for listing/browsing jobs (server-side)."""

    search: str | None = Field(default=None, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    employment_type: EmploymentType | None = None
    status: JobStatus | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort: str = Field(default="newest")
