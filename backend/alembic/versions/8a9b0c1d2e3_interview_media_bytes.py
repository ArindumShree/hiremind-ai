"""interview media bytes table

Revision ID: 8a9b0c1d2e3
Revises: 7e8f9a0b1c2
Create Date: 2026-08-01 10:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

import app.models.types

revision: str = "8a9b0c1d2e3"
down_revision: Union[str, None] = "7e8f9a0b1c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "interview_media",
        sa.Column("id", app.models.types.GUID(), nullable=False),
        sa.Column("interview_id", app.models.types.GUID(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=127), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("file_data", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["interview_id"], ["interviews.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_interview_media_interview_id"),
        "interview_media",
        ["interview_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_interview_media_interview_id"), table_name="interview_media"
    )
    op.drop_table("interview_media")
