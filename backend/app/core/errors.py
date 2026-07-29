from __future__ import annotations

from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    """Stable, machine-readable error codes for the API error envelope."""

    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    BAD_REQUEST = "BAD_REQUEST"


class AppError(Exception):
    """Base application exception carrying a standardized error envelope."""

    def __init__(
        self,
        message: str,
        *,
        code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        status_code: int = 500,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", details: Any | None = None) -> None:
        super().__init__(
            message, code=ErrorCode.NOT_FOUND, status_code=404, details=details
        )


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Not authenticated", details: Any | None = None) -> None:
        super().__init__(
            message, code=ErrorCode.UNAUTHORIZED, status_code=401, details=details
        )


class ForbiddenError(AppError):
    def __init__(self, message: str = "Not permitted", details: Any | None = None) -> None:
        super().__init__(
            message, code=ErrorCode.FORBIDDEN, status_code=403, details=details
        )


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict", details: Any | None = None) -> None:
        super().__init__(
            message, code=ErrorCode.CONFLICT, status_code=409, details=details
        )


class BadRequestError(AppError):
    def __init__(self, message: str = "Bad request", details: Any | None = None) -> None:
        super().__init__(
            message, code=ErrorCode.BAD_REQUEST, status_code=400, details=details
        )
