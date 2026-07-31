from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.types import GUID
from app.utils.time import utc_now

if TYPE_CHECKING:
    from app.models.interview import Interview


class InterviewMedia(Base):
    """A stored interview answer media file (audio/video) in the database.

    Files are stored as ``file_data`` bytes so that uploads survive on
    serverless hosts (Vercel) where the local filesystem is read-only.
    """

    __tablename__ = "interview_media"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    interview_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(127), nullable=False)
    size_bytes: Mapped[int] = mapped_column(nullable=False)
    file_data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )

    interview: Mapped[Interview] = relationship(
        back_populates="media", lazy="selectin"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"<InterviewMedia id={self.id} "
            f"interview_id={self.interview_id} filename={self.filename!r}>"
        )
