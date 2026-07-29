from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ApplicationStatus
from app.models.types import GUID
from app.utils.time import utc_now

if TYPE_CHECKING:
    from app.models.interview import Interview
    from app.models.job import Job
    from app.models.user import User


class Application(Base):
    """A candidate's application to a single job.

    A (candidate_id, job_id) pair is unique to prevent duplicate applications.
    """

    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint(
            "candidate_id", "job_id", name="uq_application_candidate_job"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        SAEnum(
            ApplicationStatus,
            name="application_status",
            native_enum=False,
            length=25,
        ),
        nullable=False,
        default=ApplicationStatus.APPLIED,
    )
    cover_letter: Mapped[str | None] = mapped_column(Text, nullable=True)
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    candidate: Mapped[User] = relationship(lazy="selectin")
    job: Mapped[Job] = relationship(back_populates="applications", lazy="selectin")
    interview: Mapped[Interview | None] = relationship(
        back_populates="application",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"<Application id={self.id} candidate_id={self.candidate_id} "
            f"job_id={self.job_id} status={self.status}>"
        )
