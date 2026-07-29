from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_current_user, require_role
from app.middleware.exceptions import register_exception_handlers
from app.models.enums import UserRole
from app.models.user import User


def _build_rbac_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/candidate-only")
    async def candidate_only(
        _user: User = Depends(require_role(UserRole.CANDIDATE)),
    ) -> dict[str, str]:
        return {"ok": "candidate"}

    @app.get("/recruiter-only")
    async def recruiter_only(
        _user: User = Depends(require_role(UserRole.RECRUITER)),
    ) -> dict[str, str]:
        return {"ok": "recruiter"}

    return app


def _fake_user(role: UserRole) -> User:
    return User(
        full_name="Test User",
        email="test@example.com",
        password_hash="x",
        role=role,
        is_active=True,
    )


@pytest.mark.parametrize(
    ("role", "path", "expected"),
    [
        (UserRole.CANDIDATE, "/candidate-only", 200),
        (UserRole.RECRUITER, "/recruiter-only", 200),
        (UserRole.RECRUITER, "/candidate-only", 403),
        (UserRole.CANDIDATE, "/recruiter-only", 403),
    ],
)
async def test_role_based_access(role: UserRole, path: str, expected: int) -> None:
    app = _build_rbac_app()
    app.dependency_overrides[get_current_user] = lambda: _fake_user(role)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(path)
    assert response.status_code == expected
