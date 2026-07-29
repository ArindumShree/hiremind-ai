from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.interview import InterviewCreate, InterviewRead, InterviewSubmit
from app.services.interview import InterviewService

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post(
    "",
    response_model=InterviewRead,
    status_code=201,
    summary="Start an interview for an application (recruiter only)",
)
async def start_interview(
    payload: InterviewCreate,
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
    session: AsyncSession = Depends(get_db),
) -> InterviewRead:
    interview = await InterviewService(session).start_for_application(
        current_user.id, payload.application_id
    )
    return InterviewRead.model_validate(interview)


@router.get(
    "/{interview_id}",
    response_model=InterviewRead,
    summary="Fetch an interview and its questions (owner candidate or job owner)",
)
async def get_interview(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> InterviewRead:
    service = InterviewService(session)
    if current_user.role == UserRole.CANDIDATE:
        interview = await service.get_for_candidate(interview_id, current_user.id)
    elif current_user.role == UserRole.RECRUITER:
        interview = await service.get_for_recruiter(interview_id, current_user.id)
    else:
        raise NotFoundError("Interview not found")
    return InterviewRead.model_validate(interview)


@router.get(
    "/{interview_id}/media",
    summary="Fetch the interview media file (owner candidate or job owner)",
)
async def get_interview_media(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Return the first stored answer media (audio/video) for playback."""
    service = InterviewService(session)
    interview = await service._resolve_for_analysis(interview_id, current_user)
    media_path = service._first_media_path(interview, ("audio", "video"))
    if not media_path or not os.path.exists(media_path):
        raise NotFoundError("No media found for this interview")
    media_type = "application/octet-stream"
    for item in interview.questions_json or []:
        if item.get("media_path") == media_path:
            media_type = item.get("media_type") or media_type
            break
    return FileResponse(
        media_path,
        media_type=media_type,
        filename=os.path.basename(media_path),
    )


@router.post(
    "/{interview_id}/submit",
    response_model=InterviewRead,
    summary="Submit interview answers (candidate owner)",
)
async def submit_interview(
    interview_id: uuid.UUID,
    payload: InterviewSubmit,
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    session: AsyncSession = Depends(get_db),
) -> InterviewRead:
    interview = await InterviewService(session).submit(
        interview_id,
        current_user.id,
        [answer.model_dump() for answer in payload.answers],
    )
    return InterviewRead.model_validate(interview)


@router.post(
    "/{interview_id}/submit/media",
    response_model=InterviewRead,
    summary="Submit interview answers with an audio/video file (candidate owner)",
)
async def submit_interview_media(
    interview_id: uuid.UUID,
    answers: str | None = None,
    file: UploadFile | None = File(default=None),
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    session: AsyncSession = Depends(get_db),
) -> InterviewRead:
    """Submit answers as JSON text plus an optional uploaded media file.

    ``answers`` is an ``InterviewSubmit`` JSON string. If a ``file`` is present,
    it is stored under ``uploads/interviews/<id>/`` and its reference is added
    as a media answer for the first question lacking one.
    """
    import json

    parsed: list[dict] = []
    if answers:
        try:
            parsed = json.loads(answers).get("answers", [])
        except (json.JSONDecodeError, AttributeError) as exc:
            raise NotFoundError("Invalid answers payload") from exc

    if file is not None:
        data = await file.read()
        service = InterviewService(session)
        stored_path = service.save_media(
            interview_id, file.filename or "answer", data
        )
        # Attach the media reference to the first answer (or create one).
        if parsed:
            parsed[0].setdefault("media_path", stored_path)
            parsed[0].setdefault(
                "media_type", file.content_type or "application/octet-stream"
            )
        else:
            parsed.append(
                {
                    "question_id": "0",
                    "text": None,
                    "media_path": stored_path,
                    "media_type": file.content_type
                    or "application/octet-stream",
                }
            )

    interview = await InterviewService(session).submit(
        interview_id, current_user.id, parsed
    )
    return InterviewRead.model_validate(interview)
