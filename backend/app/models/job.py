from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import (
    EmploymentType,
    JobStatus,
)
from app.models.types import GUID
from app.utils.time import utc_now

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.user import User


class Job(Base):
    """A job posting created by a recruiter.

    Uses a soft-delete (``deleted_at``) so that historical applications and
    hiring data are preserved even after a recruiter removes a posting.
    """

    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employment_type: Mapped[EmploymentType | None] = mapped_column(
        SAEnum(
            EmploymentType, name="employment_type", native_enum=False, length=20
        ),
        nullable=True,
    )
    experience_required: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    salary_range: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsibilities: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills_required: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        SAEnum(JobStatus, name="job_status", native_enum=False, length=20),
        nullable=False,
        default=JobStatus.DRAFT,
        index=True,
    )
    posted_by: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    poster: Mapped[User] = relationship(back_populates="jobs", lazy="selectin")
    applications: Mapped[list[Application]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Job id={self.id} title={self.title!r} status={self.status}>"
