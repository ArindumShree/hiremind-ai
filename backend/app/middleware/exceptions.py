from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.errors import AppError, ErrorCode
from app.core.logging import get_logger

logger = get_logger(__name__)


def _error_envelope(
    *,
    code: ErrorCode,
    message: str,
    status_code: int,
    details: Any | None = None,
) -> dict[str, Any]:
    """Build a consistent error response envelope."""
    return {
        "error": {
            "code": code.value,
            "message": message,
            "details": details,
        },
        "status_code": status_code,
    }


def register_exception_handlers(app: FastAPI) -> None:
    """Register centralized exception handlers on the FastAPI app."""

    @app.exception_handler(AppError)
    async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.exception("Application error: %s", exc.message)
        else:
            logger.warning("Application error (%s): %s", exc.code.value, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_envelope(
                code=exc.code,
                message=exc.message,
                status_code=exc.status_code,
                details=jsonable_encoder(exc.details) if exc.details is not None else None,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning("Validation error: %s", exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_envelope(
                code=ErrorCode.VALIDATION_ERROR,
                message="Request validation failed",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details=jsonable_encoder(exc.errors()),
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        _request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unexpected error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_envelope(
                code=ErrorCode.INTERNAL_ERROR,
                message="Internal server error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
        )
