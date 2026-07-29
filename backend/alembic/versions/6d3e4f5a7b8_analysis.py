"""analysis metrics on interviews

Revision ID: 6d3e4f5a7b8
Revises: 5c2d3e4f6a7
Create Date: 2026-07-19 22:30:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "6d3e4f5a7b8"
down_revision: Union[str, None] = "5c2d3e4f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "interviews",
        sa.Column("speech_metrics", sa.JSON(), nullable=True),
    )
    op.add_column(
        "interviews",
        sa.Column("video_metrics", sa.JSON(), nullable=True),
    )
    op.add_column(
        "interviews",
        sa.Column("evaluation", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("interviews", "evaluation")
    op.drop_column("interviews", "video_metrics")
    op.drop_column("interviews", "speech_metrics")
