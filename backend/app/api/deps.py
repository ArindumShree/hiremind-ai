from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from fastapi import Depends, Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import JWTError, decode_token
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user import UserRepository

_bearer_scheme = HTTPBearer(auto_error=False)


async def parse_job_id(job_id: str = Path(...)) -> uuid.UUID:
    """Validate and parse a job id path parameter into a UUID."""
    try:
        return uuid.UUID(job_id)
    except ValueError as exc:
        raise NotFoundError("Job not found") from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Resolve and return the authenticated user from a Bearer access token."""
    if credentials is None or not credentials.credentials:
        raise UnauthorizedError("Authentication credentials were not provided")

    try:
        claims = decode_token(credentials.credentials)
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired access token") from exc

    if claims.get("type") != "access":
        raise UnauthorizedError("Provided token is not an access token")

    subject = claims.get("sub")
    if not subject:
        raise UnauthorizedError("Malformed access token")

    user = await UserRepository(session).get_by_id(uuid.UUID(subject))
    if user is None or not user.is_active:
        raise UnauthorizedError("User no longer exists or is disabled")
    return user


def require_role(
    *roles: UserRole,
) -> Callable[[User], Awaitable[User]]:
    """Dependency factory enforcing that the current user has one of ``roles``."""

    async def _dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in roles:
            raise ForbiddenError(
                "You do not have permission to access this resource"
            )
        return current_user

    return _dependency
