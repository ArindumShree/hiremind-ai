from __future__ import annotations

from httpx import AsyncClient


async def _auth_headers(client: AsyncClient, payload: dict[str, str]) -> dict[str, str]:
    await client.post("/api/v1/auth/register", json=payload)
    tokens = (
        await client.post(
            "/api/v1/auth/login",
            json={"email": payload["email"], "password": payload["password"]},
        )
    ).json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


async def test_get_profile_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/profile")
    assert response.status_code == 401


async def test_get_profile_returns_empty_profile(
    client: AsyncClient, candidate_payload
) -> None:
    headers = await _auth_headers(client, candidate_payload)
    response = await client.get("/api/v1/profile", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["phone"] is None
    assert body["bio"] is None


async def test_update_profile(client: AsyncClient, candidate_payload) -> None:
    headers = await _auth_headers(client, candidate_payload)
    update = {
        "phone": "+1-555-0100",
        "college": "State University",
        "github_url": "https://github.com/casey",
        "bio": "Aspiring engineer.",
    }
    response = await client.put("/api/v1/profile", json=update, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["phone"] == "+1-555-0100"
    assert body["college"] == "State University"
    assert body["github_url"].startswith("https://github.com/casey")
    assert body["bio"] == "Aspiring engineer."


async def test_update_profile_invalid_url_rejected(
    client: AsyncClient, candidate_payload
) -> None:
    headers = await _auth_headers(client, candidate_payload)
    response = await client.put(
        "/api/v1/profile", json={"linkedin_url": "not-a-url"}, headers=headers
    )
    assert response.status_code == 422
