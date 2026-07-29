"""resumes

Revision ID: 4b1c2d3e5f6
Revises: 3a7f1c9d2e4
Create Date: 2026-07-19 14:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

import app.models.types

revision: str = "4b1c2d3e5f6"
down_revision: Union[str, None] = "3a7f1c9d2e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resumes",
        sa.Column("id", app.models.types.GUID(), nullable=False),
        sa.Column("candidate_id", app.models.types.GUID(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("stored_path", sa.String(length=512), nullable=False),
        sa.Column("content_type", sa.String(length=127), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["candidate_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("candidate_id", name="uq_resumes_candidate_id"),
    )
    op.create_index(
        op.f("ix_resumes_candidate_id"), "resumes", ["candidate_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_resumes_candidate_id"), table_name="resumes")
    op.drop_table("resumes")
