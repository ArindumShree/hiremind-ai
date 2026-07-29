from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import (
    JWTError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.profile import Profile
from app.models.user import User
from app.repositories.profile import ProfileRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPair
from app.utils.time import utc_now


class AuthService:
    """Business logic for authentication and token management."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._profiles = ProfileRepository(session)
        self._tokens = RefreshTokenRepository(session)

    async def register(self, payload: RegisterRequest) -> User:
        """Create a new user and an empty profile."""
        normalized_email = payload.email.lower()
        if await self._users.email_exists(normalized_email):
            raise ConflictError("An account with this email already exists")

        user = User(
            full_name=payload.full_name.strip(),
            email=normalized_email,
            password_hash=hash_password(payload.password),
            role=payload.role,
        )
        await self._users.add(user)
        await self._profiles.add(Profile(user_id=user.id))
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def authenticate(self, payload: LoginRequest) -> User:
        """Validate credentials and return the user."""
        user = await self._users.get_by_email(payload.email.lower())
        if user is None or not verify_password(
            payload.password, user.password_hash
        ):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")
        return user

    async def issue_tokens(self, user: User) -> TokenPair:
        """Create and persist a new access/refresh token pair."""
        access_token = create_access_token(
            str(user.id), extra_claims={"role": user.role.value}
        )
        refresh_token, jti = create_refresh_token(str(user.id))
        expires_at = utc_now() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        await self._tokens.add(jti=jti, user_id=user.id, expires_at=expires_at)
        await self._session.commit()
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def login(self, payload: LoginRequest) -> TokenPair:
        user = await self.authenticate(payload)
        return await self.issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        """Rotate a valid refresh token into a new token pair."""
        claims = self._decode_refresh(refresh_token)
        jti = claims["jti"]

        stored = await self._tokens.get_by_jti(jti)
        if stored is None or stored.revoked:
            raise UnauthorizedError("Refresh token is invalid or revoked")

        user = await self._users.get_by_id(uuid.UUID(claims["sub"]))
        if user is None or not user.is_active:
            raise UnauthorizedError("User no longer exists or is disabled")

        await self._tokens.revoke(jti)
        return await self.issue_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        """Revoke the given refresh token (best-effort)."""
        try:
            claims = self._decode_refresh(refresh_token)
        except UnauthorizedError:
            return
        await self._tokens.revoke(claims["jti"])
        await self._session.commit()

    @staticmethod
    def _decode_refresh(refresh_token: str) -> dict:
        try:
            claims = decode_token(refresh_token)
        except JWTError as exc:  # noqa: BLE001 - normalize into API error
            raise UnauthorizedError("Refresh token is invalid or expired") from exc
        if claims.get("type") != "refresh":
            raise UnauthorizedError("Provided token is not a refresh token")
        return claims
