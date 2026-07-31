"""store resume file bytes in the database

Revision ID: 7e8f9a0b1c2
Revises: 6d3e4f5a7b8
Create Date: 2026-08-01 09:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "7e8f9a0b1c2"
down_revision: Union[str, None] = "6d3e4f5a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "resumes",
        sa.Column("file_data", sa.LargeBinary(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("resumes", "file_data")
