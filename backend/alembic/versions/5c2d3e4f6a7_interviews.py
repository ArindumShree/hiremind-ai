"""interviews

Revision ID: 5c2d3e4f6a7
Revises: 4b1c2d3e5f6
Create Date: 2026-07-19 14:30:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

import app.models.types

revision: str = "5c2d3e4f6a7"
down_revision: Union[str, None] = "4b1c2d3e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "interviews",
        sa.Column("id", app.models.types.GUID(), nullable=False),
        sa.Column("application_id", app.models.types.GUID(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "active",
                "completed",
                name="interview_status",
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("questions_json", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["application_id"], ["applications.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("application_id", name="uq_interviews_application_id"),
    )
    op.create_index(
        op.f("ix_interviews_application_id"),
        "interviews",
        ["application_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_interviews_application_id"), table_name="interviews")
    op.drop_table("interviews")
    sa.Enum(name="interview_status").drop(op.get_bind(), checkfirst=True)
