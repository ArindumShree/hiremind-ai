from __future__ import annotations

import os
from collections.abc import AsyncGenerator

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-do-not-use-in-prod")
# Tests must never hit a live AI provider. Force the AI key empty so the
# question/evaluation services degrade gracefully; tests that exercise the AI
# path set a fake key and mock the httpx transport instead.
os.environ["NVIDIA_API_KEY"] = ""
os.environ["GEMINI_API_KEY"] = ""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app import models  # noqa: F401  (register models on Base.metadata)
from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_sessionmaker() -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
    try:
        yield maker
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def client(
    db_sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with db_sessionmaker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def candidate_payload() -> dict[str, str]:
    return {
        "full_name": "Casey Candidate",
        "email": "casey@example.com",
        "password": "StrongPass1",
        "confirm_password": "StrongPass1",
        "role": "candidate",
    }


@pytest.fixture
def recruiter_payload() -> dict[str, str]:
    return {
        "full_name": "Riley Recruiter",
        "email": "riley@example.com",
        "password": "StrongPass1",
        "confirm_password": "StrongPass1",
        "role": "recruiter",
    }


async def register_and_login(client: AsyncClient, payload: dict[str, str]) -> dict[str, str]:
    """Register a user and return their auth headers + tokens."""
    reg = await client.post("/api/v1/auth/register", json=payload)
    assert reg.status_code == 201, reg.text
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    return {
        "access_token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }
