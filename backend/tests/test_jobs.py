from __future__ import annotations

from httpx import AsyncClient

from tests.conftest import register_and_login

JOB_PAYLOAD = {
    "title": "Senior Python Engineer",
    "company_name": "Acme Corp",
    "location": "Remote",
    "employment_type": "full_time",
    "experience_required": "5 years",
    "salary_range": "120k-150k",
    "description": "Build great things.",
    "requirements": "Python, FastAPI",
    "responsibilities": "Lead backend",
    "skills_required": "Python, SQL",
}


async def _create_job(client: AsyncClient, headers: dict) -> dict:
    response = await client.post("/api/v1/jobs", json=JOB_PAYLOAD, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


async def test_recruiter_creates_job(client: AsyncClient, recruiter_payload) -> None:
    auth = await register_and_login(client, recruiter_payload)
    body = await _create_job(client, auth["headers"])
    assert body["title"] == JOB_PAYLOAD["title"]
    assert body["status"] == "draft"
    assert body["posted_by"]


async def test_candidate_cannot_create_job(
    client: AsyncClient, candidate_payload
) -> None:
    auth = await register_and_login(client, candidate_payload)
    response = await client.post(
        "/api/v1/jobs", json=JOB_PAYLOAD, headers=auth["headers"]
    )
    assert response.status_code == 403


async def test_recruiter_lists_own_jobs(
    client: AsyncClient, recruiter_payload
) -> None:
    auth = await register_and_login(client, recruiter_payload)
    await _create_job(client, auth["headers"])
    response = await client.get("/api/v1/jobs/my", headers=auth["headers"])
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_recruiter_edits_own_job(
    client: AsyncClient, recruiter_payload
) -> None:
    auth = await register_and_login(client, recruiter_payload)
    job = await _create_job(client, auth["headers"])
    response = await client.put(
        f"/api/v1/jobs/{job['id']}",
        json={"title": "Staff Engineer"},
        headers=auth["headers"],
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Staff Engineer"


async def test_recruiter_cannot_edit_others_job(
    client: AsyncClient, recruiter_payload
) -> None:
    owner = await register_and_login(client, recruiter_payload)
    job = await _create_job(client, owner["headers"])

    intruder_payload = {**recruiter_payload, "email": "other@recruiter.com"}
    intruder = await register_and_login(client, intruder_payload)
    response = await client.put(
        f"/api/v1/jobs/{job['id']}",
        json={"title": "Hijacked"},
        headers=intruder["headers"],
    )
    assert response.status_code == 404


async def test_recruiter_cannot_delete_others_job(
    client: AsyncClient, recruiter_payload
) -> None:
    owner = await register_and_login(client, recruiter_payload)
    job = await _create_job(client, owner["headers"])
    intruder = await register_and_login(
        client, {**recruiter_payload, "email": "other2@recruiter.com"}
    )
    response = await client.delete(
        f"/api/v1/jobs/{job['id']}", headers=intruder["headers"]
    )
    assert response.status_code == 404


async def test_publish_and_close_flow(
    client: AsyncClient, recruiter_payload
) -> None:
    auth = await register_and_login(client, recruiter_payload)
    job = await _create_job(client, auth["headers"])

    published = await client.patch(
        f"/api/v1/jobs/{job['id']}/publish", headers=auth["headers"]
    )
    assert published.status_code == 200
    assert published.json()["status"] == "published"

    closed = await client.patch(
        f"/api/v1/jobs/{job['id']}/close", headers=auth["headers"]
    )
    assert closed.status_code == 200
    assert closed.json()["status"] == "closed"


async def test_soft_delete_preserves_record(
    client: AsyncClient, recruiter_payload
) -> None:
    auth = await register_and_login(client, recruiter_payload)
    job = await _create_job(client, auth["headers"])
    delete = await client.delete(
        f"/api/v1/jobs/{job['id']}", headers=auth["headers"]
    )
    assert delete.status_code == 204
    # Record still exists but is marked deleted (not returned to owner list).
    listing = await client.get("/api/v1/jobs/my", headers=auth["headers"])
    assert listing.status_code == 200
    assert len(listing.json()) == 0


async def test_candidate_browses_published_jobs(
    client: AsyncClient, recruiter_payload, candidate_payload
) -> None:
    recruiter = await register_and_login(client, recruiter_payload)
    job = await _create_job(client, recruiter["headers"])
    # Draft job is not visible to candidates.
    browse = await client.get("/api/v1/jobs")
    assert browse.status_code == 200
    assert browse.json()["meta"]["total"] == 0

    await client.patch(
        f"/api/v1/jobs/{job['id']}/publish", headers=recruiter["headers"]
    )
    browse = await client.get("/api/v1/jobs")
    assert browse.status_code == 200
    assert browse.json()["meta"]["total"] == 1


async def test_search_and_filter(
    client: AsyncClient, recruiter_payload
) -> None:
    recruiter = await register_and_login(client, recruiter_payload)
    job1 = await _create_job(client, recruiter["headers"])
    job2 = await client.post(
        "/api/v1/jobs",
        json={**JOB_PAYLOAD, "title": "Frontend Dev", "company_name": "Globex"},
        headers=recruiter["headers"],
    )
    job2_id = job2.json()["id"]
    # Publish both so they are visible to browsers.
    await client.patch(
        f"/api/v1/jobs/{job1['id']}/publish", headers=recruiter["headers"]
    )
    await client.patch(
        f"/api/v1/jobs/{job2_id}/publish", headers=recruiter["headers"]
    )

    by_title = await client.get("/api/v1/jobs?search=Frontend")
    assert by_title.json()["meta"]["total"] == 1
    assert by_title.json()["items"][0]["company_name"] == "Globex"

    by_company = await client.get("/api/v1/jobs?search=Acme")
    assert by_company.json()["meta"]["total"] == 1

    no_match = await client.get("/api/v1/jobs?search=zzz")
    assert no_match.json()["meta"]["total"] == 0


async def test_pagination(
    client: AsyncClient, recruiter_payload
) -> None:
    recruiter = await register_and_login(client, recruiter_payload)
    for i in range(3):
        await client.post(
            "/api/v1/jobs",
            json={**JOB_PAYLOAD, "title": f"Job {i}"},
            headers=recruiter["headers"],
        )
    # Publish all three.
    jobs = await client.get("/api/v1/jobs/my", headers=recruiter["headers"])
    for j in jobs.json():
        await client.patch(
            f"/api/v1/jobs/{j['id']}/publish", headers=recruiter["headers"]
        )
    page = await client.get("/api/v1/jobs?page=1&page_size=2")
    assert page.json()["meta"]["page_size"] == 2
    assert page.json()["meta"]["total"] == 3
    assert len(page.json()["items"]) == 2


async def test_candidate_applies(
    client: AsyncClient, recruiter_payload, candidate_payload
) -> None:
    recruiter = await register_and_login(client, recruiter_payload)
    job = await _create_job(client, recruiter["headers"])
    await client.patch(
        f"/api/v1/jobs/{job['id']}/publish", headers=recruiter["headers"]
    )
    candidate = await register_and_login(client, candidate_payload)
    response = await client.post(
        f"/api/v1/jobs/{job['id']}/apply",
        json={"cover_letter": "Hi!"},
        headers=candidate["headers"],
    )
    assert response.status_code == 201
    assert response.json()["status"] == "applied"


async def test_duplicate_application_prevented(
    client: AsyncClient, recruiter_payload, candidate_payload
) -> None:
    recruiter = await register_and_login(client, recruiter_payload)
    job = await _create_job(client, recruiter["headers"])
    await client.patch(
        f"/api/v1/jobs/{job['id']}/publish", headers=recruiter["headers"]
    )
    candidate = await register_and_login(client, candidate_payload)
    first = await client.post(
        f"/api/v1/jobs/{job['id']}/apply",
        json={"cover_letter": "Hi!"},
        headers=candidate["headers"],
    )
    assert first.status_code == 201
    second = await client.post(
        f"/api/v1/jobs/{job['id']}/apply",
        json={"cover_letter": "Hi!"},
        headers=candidate["headers"],
    )
    assert second.status_code == 400


async def test_cannot_apply_to_closed_job(
    client: AsyncClient, recruiter_payload, candidate_payload
) -> None:
    recruiter = await register_and_login(client, recruiter_payload)
    job = await _create_job(client, recruiter["headers"])
    await client.patch(
        f"/api/v1/jobs/{job['id']}/publish", headers=recruiter["headers"]
    )
    await client.patch(
        f"/api/v1/jobs/{job['id']}/close", headers=recruiter["headers"]
    )
    candidate = await register_and_login(client, candidate_payload)
    response = await client.post(
        f"/api/v1/jobs/{job['id']}/apply",
        json={"cover_letter": "Hi!"},
        headers=candidate["headers"],
    )
    assert response.status_code == 400


async def test_recruiter_views_applicants(
    client: AsyncClient, recruiter_payload, candidate_payload
) -> None:
    recruiter = await register_and_login(client, recruiter_payload)
    job = await _create_job(client, recruiter["headers"])
    await client.patch(
        f"/api/v1/jobs/{job['id']}/publish", headers=recruiter["headers"]
    )
    candidate = await register_and_login(client, candidate_payload)
    await client.post(
        f"/api/v1/jobs/{job['id']}/apply",
        json={"cover_letter": "Hi!"},
        headers=candidate["headers"],
    )
    applicants = await client.get(
        f"/api/v1/jobs/{job['id']}/applications", headers=recruiter["headers"]
    )
    assert applicants.status_code == 200
    assert len(applicants.json()) == 1
    assert applicants.json()[0]["candidate"]["email"] == candidate_payload["email"]


async def test_candidate_views_own_applications(
    client: AsyncClient, recruiter_payload, candidate_payload
) -> None:
    recruiter = await register_and_login(client, recruiter_payload)
    job = await _create_job(client, recruiter["headers"])
    await client.patch(
        f"/api/v1/jobs/{job['id']}/publish", headers=recruiter["headers"]
    )
    candidate = await register_and_login(client, candidate_payload)
    await client.post(
        f"/api/v1/jobs/{job['id']}/apply",
        json={"cover_letter": "Hi!"},
        headers=candidate["headers"],
    )
    mine = await client.get(
        "/api/v1/applications/my", headers=candidate["headers"]
    )
    assert mine.status_code == 200
    assert len(mine.json()) == 1
    assert mine.json()[0]["job_id"] == job["id"]


async def test_candidate_cannot_view_applicants(
    client: AsyncClient, recruiter_payload, candidate_payload
) -> None:
    recruiter = await register_and_login(client, recruiter_payload)
    job = await _create_job(client, recruiter["headers"])
    candidate = await register_and_login(client, candidate_payload)
    response = await client.get(
        f"/api/v1/jobs/{job['id']}/applications", headers=candidate["headers"]
    )
    assert response.status_code == 403


async def test_recruiter_cannot_apply(
    client: AsyncClient, recruiter_payload
) -> None:
    recruiter = await register_and_login(client, recruiter_payload)
    job = await _create_job(client, recruiter["headers"])
    await client.patch(
        f"/api/v1/jobs/{job['id']}/publish", headers=recruiter["headers"]
    )
    response = await client.post(
        f"/api/v1/jobs/{job['id']}/apply",
        json={"cover_letter": "Hi!"},
        headers=recruiter["headers"],
    )
    assert response.status_code == 403
