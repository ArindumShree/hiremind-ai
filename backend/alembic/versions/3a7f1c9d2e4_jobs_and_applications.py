"""jobs_and_applications

Revision ID: 3a7f1c9d2e4
Revises: 78b2ad2e40bb
Create Date: 2026-07-19 10:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

import app.models.types

revision: str = "3a7f1c9d2e4"
down_revision: Union[str, None] = "78b2ad2e40bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", app.models.types.GUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column(
            "employment_type",
            sa.Enum(
                "FULL_TIME",
                "PART_TIME",
                "CONTRACT",
                "INTERN",
                "FREELANCE",
                name="employment_type",
                native_enum=False,
                length=20,
            ),
            nullable=True,
        ),
        sa.Column("experience_required", sa.String(length=255), nullable=True),
        sa.Column("salary_range", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column("responsibilities", sa.Text(), nullable=True),
        sa.Column("skills_required", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "PUBLISHED",
                "CLOSED",
                "ARCHIVED",
                name="job_status",
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("posted_by", app.models.types.GUID(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["posted_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_jobs_posted_by"), "jobs", ["posted_by"], unique=False)
    op.create_index(op.f("ix_jobs_status"), "jobs", ["status"], unique=False)

    op.create_table(
        "applications",
        sa.Column("id", app.models.types.GUID(), nullable=False),
        sa.Column("candidate_id", app.models.types.GUID(), nullable=False),
        sa.Column("job_id", app.models.types.GUID(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "APPLIED",
                "SHORTLISTED",
                "INTERVIEW_SCHEDULED",
                "INTERVIEW_COMPLETED",
                "REJECTED",
                "HIRED",
                name="application_status",
                native_enum=False,
                length=25,
            ),
            nullable=False,
        ),
        sa.Column("cover_letter", sa.Text(), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["candidate_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "candidate_id", "job_id", name="uq_application_candidate_job"
        ),
    )
    op.create_index(
        op.f("ix_applications_candidate_id"),
        "applications",
        ["candidate_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_applications_job_id"), "applications", ["job_id"], unique=False
    )
    op.create_index(
        op.f("ix_applications_applied_at"),
        "applications",
        ["applied_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_applications_applied_at"), table_name="applications")
    op.drop_index(op.f("ix_applications_job_id"), table_name="applications")
    op.drop_index(
        op.f("ix_applications_candidate_id"), table_name="applications"
    )
    op.drop_table("applications")
    op.drop_index(op.f("ix_jobs_status"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_posted_by"), table_name="jobs")
    op.drop_table("jobs")
