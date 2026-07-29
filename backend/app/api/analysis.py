from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.analysis import Evaluation, SpeechMetrics, VideoMetrics
from app.services.interview import InterviewService

router = APIRouter(prefix="/interviews", tags=["analysis"])


@router.post(
    "/{interview_id}/speech-analysis",
    response_model=SpeechMetrics,
    summary="Transcribe + analyze audio (owner candidate or job owner)",
)
async def analyze_speech(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> SpeechMetrics:
    interview = await InterviewService(session).run_speech_analysis(
        interview_id, current_user
    )
    return SpeechMetrics.model_validate(interview.speech_metrics)


@router.post(
    "/{interview_id}/video-analysis",
    response_model=VideoMetrics,
    summary="Analyze candidate video (owner candidate or job owner)",
)
async def analyze_video(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> VideoMetrics:
    interview = await InterviewService(session).run_video_analysis(
        interview_id, current_user
    )
    return VideoMetrics.model_validate(interview.video_metrics)


@router.post(
    "/{interview_id}/evaluate",
    response_model=Evaluation,
    summary="Produce a combined evaluation (owner candidate or job owner)",
)
async def evaluate_interview(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Evaluation:
    interview = await InterviewService(session).run_evaluation(
        interview_id, current_user
    )
    return Evaluation.model_validate(interview.evaluation)


@router.get(
    "/{interview_id}/evaluation",
    response_model=Evaluation,
    summary="Fetch the stored evaluation (owner candidate or job owner)",
)
async def get_evaluation(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Evaluation:
    service = InterviewService(session)
    interview = await service._resolve_for_analysis(interview_id, current_user)
    if not interview.evaluation:
        interview = await service.run_evaluation(interview_id, current_user)
    return Evaluation.model_validate(interview.evaluation)
