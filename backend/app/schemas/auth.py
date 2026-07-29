from __future__ import annotations

import re

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.models.enums import UserRole

_PASSWORD_MIN_LENGTH = 8
_PASSWORD_MAX_LENGTH = 128


def validate_password_strength(password: str) -> str:
    """Validate password against modern strength rules.

    Rules: length 8-128, at least one lowercase, one uppercase, and one digit.
    """
    if len(password) < _PASSWORD_MIN_LENGTH:
        raise ValueError(
            f"Password must be at least {_PASSWORD_MIN_LENGTH} characters long"
        )
    if len(password) > _PASSWORD_MAX_LENGTH:
        raise ValueError(
            f"Password must be at most {_PASSWORD_MAX_LENGTH} characters long"
        )
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain a lowercase letter")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain an uppercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain a digit")
    return password


class RegisterRequest(BaseModel):
    """Payload for creating a new account."""

    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=_PASSWORD_MIN_LENGTH, max_length=_PASSWORD_MAX_LENGTH)
    confirm_password: str
    role: UserRole

    @field_validator("password")
    @classmethod
    def _check_password_strength(cls, value: str) -> str:
        return validate_password_strength(value)

    @model_validator(mode="after")
    def _check_passwords_match(self) -> RegisterRequest:
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginRequest(BaseModel):
    """Payload for authenticating with email and password."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Payload carrying a refresh token."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Payload carrying the refresh token to revoke."""

    refresh_token: str


class TokenPair(BaseModel):
    """Access + refresh token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
