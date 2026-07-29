from __future__ import annotations

from httpx import AsyncClient


async def _register(client: AsyncClient, payload: dict[str, str]) -> None:
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text


async def _login(client: AsyncClient, email: str, password: str) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()


async def test_register_creates_user(client: AsyncClient, candidate_payload) -> None:
    response = await client.post("/api/v1/auth/register", json=candidate_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == candidate_payload["email"]
    assert body["role"] == "candidate"
    assert body["is_active"] is True
    assert "password" not in body
    assert "password_hash" not in body


async def test_register_duplicate_email_conflicts(
    client: AsyncClient, candidate_payload
) -> None:
    await _register(client, candidate_payload)
    response = await client.post("/api/v1/auth/register", json=candidate_payload)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


async def test_register_password_mismatch_rejected(
    client: AsyncClient, candidate_payload
) -> None:
    payload = {**candidate_payload, "confirm_password": "Different1"}
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


async def test_register_weak_password_rejected(
    client: AsyncClient, candidate_payload
) -> None:
    payload = {**candidate_payload, "password": "weak", "confirm_password": "weak"}
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


async def test_login_returns_tokens(client: AsyncClient, candidate_payload) -> None:
    await _register(client, candidate_payload)
    tokens = await _login(
        client, candidate_payload["email"], candidate_payload["password"]
    )
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"


async def test_login_invalid_credentials(
    client: AsyncClient, candidate_payload
) -> None:
    await _register(client, candidate_payload)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": candidate_payload["email"], "password": "WrongPass1"},
    )
    assert response.status_code == 401


async def test_me_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_me_returns_current_user(
    client: AsyncClient, candidate_payload
) -> None:
    await _register(client, candidate_payload)
    tokens = await _login(
        client, candidate_payload["email"], candidate_payload["password"]
    )
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == candidate_payload["email"]
    assert "profile" in body


async def test_me_rejects_invalid_token(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-token"}
    )
    assert response.status_code == 401


async def test_refresh_rotates_tokens(
    client: AsyncClient, candidate_payload
) -> None:
    await _register(client, candidate_payload)
    tokens = await _login(
        client, candidate_payload["email"], candidate_payload["password"]
    )
    response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert response.status_code == 200
    new_tokens = response.json()
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    # Old refresh token is now revoked.
    reuse = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert reuse.status_code == 401


async def test_logout_revokes_refresh_token(
    client: AsyncClient, candidate_payload
) -> None:
    await _register(client, candidate_payload)
    tokens = await _login(
        client, candidate_payload["email"], candidate_payload["password"]
    )
    logout = await client.post(
        "/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]}
    )
    assert logout.status_code == 204

    refresh = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh.status_code == 401
