from __future__ import annotations

from httpx import AsyncClient

from tests.conftest import register_and_login

JOB_PAYLOAD = {
    "title": "Senior Python Engineer",
    "company_name": "Acme Corp",
    "location": "Remote",
    "employment_type": "full_time",
    "experience_required": "5 years",
    "description": "Build great things.",
    "requirements": "Python, FastAPI",
    "skills_required": "Python, SQL",
}


async def _create_job(client: AsyncClient, headers: dict) -> dict:
    response = await client.post("/api/v1/jobs", json=JOB_PAYLOAD, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


async def _publish_job(client: AsyncClient, job_id: str, headers: dict) -> None:
    response = await client.patch(
        f"/api/v1/jobs/{job_id}/publish", headers=headers
    )
    assert response.status_code == 200, response.text


async def _apply(client: AsyncClient, job_id: str, headers: dict) -> dict:
    response = await client.post(
        f"/api/v1/jobs/{job_id}/apply",
        json={"cover_letter": "Hi"},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _setup_interview(
    client: AsyncClient,
) -> tuple[dict, dict, dict]:
    """Return (recruiter_auth, candidate_auth, interview_json)."""
    recruiter = await register_and_login(client, _recruiter_payload())
    candidate = await register_and_login(client, _candidate_payload())

    job = await _create_job(client, recruiter["headers"])
    await _publish_job(client, job["id"], recruiter["headers"])
    application = await _apply(client, job["id"], candidate["headers"])

    # Recruiter shortlists the application.
    patch = await client.patch(
        f"/api/v1/applications/{application['id']}/status",
        json={"status": "shortlisted"},
        headers=recruiter["headers"],
    )
    assert patch.status_code == 200, patch.text

    # Recruiter starts the interview.
    start = await client.post(
        "/api/v1/interviews",
        json={"application_id": application["id"]},
        headers=recruiter["headers"],
    )
    assert start.status_code == 201, start.text
    return recruiter, candidate, start.json()


def _recruiter_payload() -> dict:
    return {
        "full_name": "Riley Recruiter",
        "email": "riley@example.com",
        "password": "StrongPass1",
        "confirm_password": "StrongPass1",
        "role": "recruiter",
    }


def _candidate_payload() -> dict:
    return {
        "full_name": "Casey Candidate",
        "email": "casey@example.com",
        "password": "StrongPass1",
        "confirm_password": "StrongPass1",
        "role": "candidate",
    }


async def test_recruiter_starts_interview(client: AsyncClient) -> None:
    _, _, interview = await _setup_interview(client)
    assert interview["status"] == "active"
    assert interview["application_id"]
    assert isinstance(interview["questions"], list)
    assert len(interview["questions"]) > 0


async def test_candidate_fetches_interview(client: AsyncClient) -> None:
    _, candidate, interview = await _setup_interview(client)
    response = await client.get(
        f"/api/v1/interviews/{interview['id']}",
        headers=candidate["headers"],
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["id"] == interview["id"]
    assert len(body["questions"]) > 0


async def test_candidate_submits_text_answers(client: AsyncClient) -> None:
    _, candidate, interview = await _setup_interview(client)
    answers = [
        {"question_id": q["id"], "text": "My answer"}
        for q in interview["questions"]
    ]
    response = await client.post(
        f"/api/v1/interviews/{interview['id']}/submit",
        json={"answers": answers},
        headers=candidate["headers"],
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "completed"
    assert body["submitted_at"] is not None


async def test_candidate_submits_with_media(client: AsyncClient) -> None:
    _, candidate, interview = await _setup_interview(client)
    answers = {
        "answers": [
            {"question_id": interview["questions"][0]["id"], "text": "Verbally"}
        ]
    }
    files = {
        "answers": (None, __import__("json").dumps(answers)),
        "file": ("answer.mp3", b"fake-audio-bytes", "audio/mpeg"),
    }
    response = await client.post(
        f"/api/v1/interviews/{interview['id']}/submit/media",
        files=files,
        headers=candidate["headers"],
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "completed"


async def test_wrong_candidate_forbidden(client: AsyncClient) -> None:
    _, candidate, interview = await _setup_interview(client)
    intruder_payload = {
        "full_name": "Other Candidate",
        "email": "other@example.com",
        "password": "StrongPass1",
        "confirm_password": "StrongPass1",
        "role": "candidate",
    }
    intruder = await register_and_login(client, intruder_payload)
    response = await client.get(
        f"/api/v1/interviews/{interview['id']}",
        headers=intruder["headers"],
    )
    assert response.status_code == 404


async def test_missing_interview_404(client: AsyncClient) -> None:
    candidate = await register_and_login(client, _candidate_payload())
    import uuid

    response = await client.get(
        f"/api/v1/interviews/{uuid.uuid4()}",
        headers=candidate["headers"],
    )
    assert response.status_code == 404


async def test_application_transitions_to_scheduled(client: AsyncClient) -> None:
    recruiter, candidate, interview = await _setup_interview(client)
    app_id = interview["application_id"]

    # Find the job_id from the candidate's own applications list.
    my_resp = await client.get(
        "/api/v1/applications/my", headers=candidate["headers"]
    )
    assert my_resp.status_code == 200, my_resp.text
    job_id = next(
        a["job_id"] for a in my_resp.json() if a["id"] == app_id
    )

    apps_resp = await client.get(
        f"/api/v1/jobs/{job_id}/applications", headers=recruiter["headers"]
    )
    assert apps_resp.status_code == 200, apps_resp.text
    apps = apps_resp.json()
    match = next((a for a in apps if a["id"] == app_id), None)
    assert match is not None
    assert match["status"] in ("interview_scheduled", "interview_completed")
