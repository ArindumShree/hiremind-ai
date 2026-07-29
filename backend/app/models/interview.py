from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import InterviewStatus
from app.models.types import GUID
from app.utils.time import utc_now

if TYPE_CHECKING:
    from app.models.application import Application


class Interview(Base):
    """An interview session for a single application.

    One interview per application (unique application_id). Stores the
    delivered questions and captured answers as a JSON blob.
    """

    __tablename__ = "interviews"
    __table_args__ = (
        UniqueConstraint(
            "application_id", name="uq_interviews_application_id"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[InterviewStatus] = mapped_column(
        SAEnum(
            InterviewStatus,
            name="interview_status",
            native_enum=False,
            length=20,
        ),
        nullable=False,
        default=InterviewStatus.PENDING,
    )
    questions_json: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON, nullable=True
    )
    speech_metrics: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )
    video_metrics: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )
    evaluation: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
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

    application: Mapped[Application] = relationship(
        back_populates="interview", lazy="selectin"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"<Interview id={self.id} application_id={self.application_id} "
            f"status={self.status}>"
        )
