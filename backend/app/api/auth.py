from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
)
from app.schemas.user import UserRead, UserWithProfile
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db),
) -> User:
    return await AuthService(session).register(payload)


@router.post("/login", response_model=TokenPair, summary="Log in")
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> TokenPair:
    return await AuthService(session).login(payload)


@router.post("/refresh", response_model=TokenPair, summary="Refresh tokens")
async def refresh(
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_db),
) -> TokenPair:
    return await AuthService(session).refresh(payload.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out (revoke refresh token)",
)
async def logout(
    payload: LogoutRequest,
    session: AsyncSession = Depends(get_db),
) -> None:
    await AuthService(session).logout(payload.refresh_token)


@router.get(
    "/me",
    response_model=UserWithProfile,
    summary="Get the current authenticated user",
)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
