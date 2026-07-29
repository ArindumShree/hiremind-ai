from __future__ import annotations

import pytest

from tests.conftest import register_and_login


async def _make_recruiter(client, email="riley@example.com"):
    return await register_and_login(
        client,
        {
            "full_name": "Riley Recruiter",
            "email": email,
            "password": "StrongPass1",
            "confirm_password": "StrongPass1",
            "role": "recruiter",
        },
    )


async def _make_candidate(client, email="casey@example.com"):
    return await register_and_login(
        client,
        {
            "full_name": "Casey Candidate",
            "email": email,
            "password": "StrongPass1",
            "confirm_password": "StrongPass1",
            "role": "candidate",
        },
    )


async def _setup_job_and_application(client, recruiter, candidate):
    """Create a published job owned by ``recruiter`` and an application by ``candidate``."""
    job = await client.post(
        "/api/v1/jobs",
        json={
            "title": "Backend Engineer",
            "company_name": "Acme",
            "location": "Remote",
            "skills_required": "Python, FastAPI, SQL",
            "description": "Build APIs",
        },
        headers=recruiter["headers"],
    )
    assert job.status_code == 201, job.text
    job_id = job.json()["id"]

    published = await client.patch(
        f"/api/v1/jobs/{job_id}/publish", headers=recruiter["headers"]
    )
    assert published.status_code == 200, published.text

    application = await client.post(
        f"/api/v1/jobs/{job_id}/apply",
        json={"cover_letter": "I am great"},
        headers=candidate["headers"],
    )
    assert application.status_code == 201, application.text
    return job_id, application.json()["id"]


async def _make_profile(
    client,
    candidate,
    bio="5 years building Python and FastAPI apps.",
    college="State University",
):
    # Profile is created on register; update via the profile endpoint.
    resp = await client.get("/api/v1/profile", headers=candidate["headers"])
    if resp.status_code == 200 and resp.json().get("id"):
        await client.put(
            "/api/v1/profile",
            json={"bio": bio, "college": college},
            headers=candidate["headers"],
        )


@pytest.mark.asyncio
async def test_recruiter_lists_own_candidates(client):
    recruiter = await _make_recruiter(client)
    candidate = await _make_candidate(client)
    job_id, application_id = await _setup_job_and_application(
        client, recruiter, candidate
    )
    await _make_profile(client, candidate)

    resp = await client.get(
        "/api/v1/candidates", headers=recruiter["headers"]
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "Casey Candidate"
    assert data[0]["job_title"] == "Backend Engineer"
    assert data[0]["application_id"] == application_id
    assert "Python" in data[0]["skills"]


@pytest.mark.asyncio
async def test_other_recruiter_forbidden(client):
    recruiter = await _make_recruiter(client)
    other = await _make_recruiter(client, email="other@example.com")
    candidate = await _make_candidate(client)
    await _setup_job_and_application(client, recruiter, candidate)

    resp = await client.get(
        "/api/v1/candidates", headers=other["headers"]
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_candidate_cannot_access(client):
    recruiter = await _make_recruiter(client)
    candidate = await _make_candidate(client)
    await _setup_job_and_application(client, recruiter, candidate)

    resp = await client.get(
        "/api/v1/candidates", headers=candidate["headers"]
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_candidate_detail_fetch(client):
    recruiter = await _make_recruiter(client)
    candidate = await _make_candidate(client)
    job_id, application_id = await _setup_job_and_application(
        client, recruiter, candidate
    )
    await _make_profile(client, candidate)

    resp = await client.get(
        f"/api/v1/candidates/{application_id}", headers=recruiter["headers"]
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["application_id"] == application_id
    assert data["cover_letter"] == "I am great"
    assert data["profile"] is not None
    assert data["profile"]["college"] == "State University"


@pytest.mark.asyncio
async def test_candidate_detail_other_recruiter_404(client):
    recruiter = await _make_recruiter(client)
    other = await _make_recruiter(client, email="other@example.com")
    candidate = await _make_candidate(client)
    job_id, application_id = await _setup_job_and_application(
        client, recruiter, candidate
    )

    resp = await client.get(
        f"/api/v1/candidates/{application_id}", headers=other["headers"]
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_compare_two_candidates(client):
    recruiter = await _make_recruiter(client)
    candidate_a = await _make_candidate(client, email="a@example.com")
    candidate_b = await _make_candidate(client, email="b@example.com")
    job_id, app_a = await _setup_job_and_application(
        client, recruiter, candidate_a
    )
    # Second candidate applies to same job.
    app_b = await client.post(
        f"/api/v1/jobs/{job_id}/apply",
        json={"cover_letter": "Pick me"},
        headers=candidate_b["headers"],
    )
    assert app_b.status_code == 201, app_b.text
    app_b_id = app_b.json()["id"]

    resp = await client.post(
        "/api/v1/candidates/compare",
        json={"application_ids": [app_a, app_b_id]},
        headers=recruiter["headers"],
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data["candidates"]) == 2


@pytest.mark.asyncio
async def test_compare_missing_application_404(client):
    recruiter = await _make_recruiter(client)
    import uuid

    resp = await client.post(
        "/api/v1/candidates/compare",
        json={"application_ids": [str(uuid.uuid4())]},
        headers=recruiter["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_json_report_download(client):
    recruiter = await _make_recruiter(client)
    candidate = await _make_candidate(client)
    job_id, application_id = await _setup_job_and_application(
        client, recruiter, candidate
    )
    await _make_profile(client, candidate)

    resp = await client.get(
        f"/api/v1/candidates/{application_id}/report",
        headers=recruiter["headers"],
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["candidate_name"] == "Casey Candidate"
    assert data["job_title"] == "Backend Engineer"
    assert "generated_at" in data


@pytest.mark.asyncio
async def test_report_pdf_falls_back_to_json(client):
    recruiter = await _make_recruiter(client)
    candidate = await _make_candidate(client)
    job_id, application_id = await _setup_job_and_application(
        client, recruiter, candidate
    )

    resp = await client.get(
        f"/api/v1/candidates/{application_id}/report/pdf",
        headers=recruiter["headers"],
    )
    # reportlab is not installed in this env -> JSON fallback.
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["format"] == "json"
    assert data["report"]["candidate_name"] == "Casey Candidate"


@pytest.mark.asyncio
async def test_detail_missing_404(client):
    recruiter = await _make_recruiter(client)
    import uuid

    resp = await client.get(
        f"/api/v1/candidates/{uuid.uuid4()}", headers=recruiter["headers"]
    )
    assert resp.status_code == 404
