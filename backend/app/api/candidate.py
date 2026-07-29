from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.models.enums import ApplicationStatus, UserRole
from app.models.user import User
from app.schemas.candidate import (
    CandidateComparison,
    CandidateDetail,
    CandidateReport,
    CandidateSummary,
    CompareRequest,
)
from app.services.candidate import CandidateService

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get(
    "",
    response_model=list[CandidateSummary],
    dependencies=[Depends(require_role(UserRole.RECRUITER))],
    summary="List candidates who applied to the recruiter's jobs",
)
async def list_candidates(
    job_id: uuid.UUID | None = Query(default=None, description="Filter by job"),
    status: ApplicationStatus | None = Query(default=None),
    search: str | None = Query(default=None, description="Match name or email"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await CandidateService(session).list_for_recruiter(
        current_user.id, job_id=job_id, status=status, search=search
    )


@router.get(
    "/{application_id}",
    response_model=CandidateDetail,
    dependencies=[Depends(require_role(UserRole.RECRUITER))],
    summary="Get full candidate detail (owner only)",
)
async def get_candidate(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    return await CandidateService(session).get_detail(
        application_id, current_user.id
    )


@router.post(
    "/compare",
    response_model=CandidateComparison,
    dependencies=[Depends(require_role(UserRole.RECRUITER))],
    summary="Compare two or more candidates side-by-side",
)
async def compare_candidates(
    payload: CompareRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    return await CandidateService(session).compare(
        current_user.id, payload.application_ids
    )


@router.get(
    "/{application_id}/report",
    response_model=CandidateReport,
    dependencies=[Depends(require_role(UserRole.RECRUITER))],
    summary="Download a candidate report as JSON (owner only)",
)
async def get_candidate_report(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    return await CandidateService(session).build_report(
        application_id, current_user.id
    )


@router.get(
    "/{application_id}/report/pdf",
    dependencies=[Depends(require_role(UserRole.RECRUITER))],
    summary="Download a candidate report as PDF (falls back to JSON if unavailable)",
)
async def get_candidate_report_pdf(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Response:
    report = await CandidateService(session).build_report(
        application_id, current_user.id
    )
    try:
        from app.services.candidate_report import build_pdf_bytes

        pdf_bytes = build_pdf_bytes(report)
    except ImportError:
        import json

        report_json = json.loads(
            CandidateReport.model_validate(report).model_dump_json()
        )
        return Response(
            content=json.dumps(
                {
                    "format": "json",
                    "note": (
                        "PDF generation is not available in this environment. "
                        "Falling back to a JSON report."
                    ),
                    "report": report_json,
                }
            ),
            media_type="application/json",
            status_code=status.HTTP_200_OK,
        )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f"attachment; filename=candidate_{report['candidate_id']}.pdf"
            )
        },
    )
