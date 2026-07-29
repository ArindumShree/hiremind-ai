from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.types import GUID
from app.utils.time import utc_now

if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(Base):
    """A persisted, revocable refresh token bound to a user.

    The raw JWT is never stored. Only its unique ``jti`` claim is persisted so
    tokens can be revoked (logout) and rotated (refresh).
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    jti: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )

    user: Mapped[User] = relationship(back_populates="refresh_tokens")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<RefreshToken jti={self.jti} revoked={self.revoked}>"
