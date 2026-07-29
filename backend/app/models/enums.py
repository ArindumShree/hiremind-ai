from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    """Supported user roles for role-based access control."""

    CANDIDATE = "candidate"
    RECRUITER = "recruiter"


class JobStatus(str, Enum):
    """Lifecycle status of a job posting."""

    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    ARCHIVED = "archived"


class EmploymentType(str, Enum):
    """Standard employment type classifications."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"
    FREELANCE = "freelance"


class ApplicationStatus(str, Enum):
    """Lifecycle status of a candidate's job application."""

    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    REJECTED = "rejected"
    HIRED = "hired"


class InterviewStatus(str, Enum):
    """Lifecycle status of an interview session."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
