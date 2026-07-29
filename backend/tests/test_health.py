import os

os.environ.setdefault("ENVIRONMENT", "test")

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint_returns_status() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "hiremind-ai-backend"
    assert "database" in payload
