from __future__ import annotations

import uuid

import pytest
from httpx import MockTransport, Request, Response

from app.config.settings import settings
from app.core.errors import BadRequestError
from app.services.question import (
    QuestionService,
    build_prompt,
    parse_questions,
)
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


def _fake_job(**overrides) -> object:
    fields = {
        "title": "Engineer",
        "company_name": "Acme",
        "employment_type": None,
        "experience_required": None,
        "description": None,
        "requirements": None,
        "responsibilities": None,
        "skills_required": None,
    }
    fields.update(overrides)
    return type("Job", (), fields)()


def _nvidia_transport(content: str) -> MockTransport:
    def handler(request: Request) -> Response:
        body = {
            "choices": [
                {"message": {"role": "assistant", "content": content}}
            ]
        }
        return Response(200, json=body)

    return MockTransport(handler)


async def test_parse_questions_strips_numbering() -> None:
    raw = "1. First question\n2) Second question\n\n3. Third\n\n\n"
    result = parse_questions(raw)
    assert [q["text"] for q in result] == [
        "First question",
        "Second question",
        "Third",
    ]
    assert all(q["category"] is None for q in result)


async def test_service_returns_clean_list(monkeypatch, fake_model_text) -> None:
    import httpx

    monkeypatch.setattr(settings, "NVIDIA_API_KEY", "fake-key")
    transport = _nvidia_transport(fake_model_text)
    orig_init = httpx.AsyncClient.__init__

    def fake_init(self, *args, **kwargs):
        kwargs.pop("transport", None)
        kwargs.pop("base_url", None)
        return orig_init(self, transport=transport, base_url="http://test")

    monkeypatch.setattr(httpx.AsyncClient, "__init__", fake_init)

    service = QuestionService()
    job = _fake_job(title="Backend Engineer")
    result = await service.generate(job)
    assert [q["text"] for q in result] == [
        "First question",
        "Second question",
        "Third question",
    ]


async def test_service_raises_without_api_key(monkeypatch) -> None:
    monkeypatch.setattr(settings, "NVIDIA_API_KEY", "")
    service = QuestionService()
    job = _fake_job(title="Engineer")
    with pytest.raises(BadRequestError):
        await service.generate(job)


def test_build_prompt_role_aware() -> None:
    job = _fake_job(title="Product Designer")
    prompt = build_prompt(job)
    assert "Product Designer" in prompt
    assert "design" in prompt.lower() or "designer" in prompt.lower()


async def test_generate_endpoint_requires_api_key(
    client, candidate_payload, recruiter_payload
) -> None:
    candidate = await register_and_login(client, candidate_payload)
    recruiter = await register_and_login(client, recruiter_payload)
    job = await client.post(
        "/api/v1/jobs", json=JOB_PAYLOAD, headers=recruiter["headers"]
    )
    job_id = job.json()["id"]

    import app.config.settings as settings_mod

    original = settings_mod.settings.NVIDIA_API_KEY
    settings_mod.settings.NVIDIA_API_KEY = ""
    try:
        response = await client.post(
            "/api/v1/questions/generate",
            json={"job_id": job_id},
            headers=candidate["headers"],
        )
        assert response.status_code == 400
    finally:
        settings_mod.settings.NVIDIA_API_KEY = original


async def test_generate_endpoint_404_unknown_job(
    client, candidate_payload
) -> None:
    candidate = await register_and_login(client, candidate_payload)
    fake_id = str(uuid.uuid4())
    response = await client.post(
        "/api/v1/questions/generate",
        json={"job_id": fake_id},
        headers=candidate["headers"],
    )
    assert response.status_code == 404


async def test_generate_endpoint_returns_questions(
    client, candidate_payload, recruiter_payload, monkeypatch
) -> None:
    # Patch the httpx client used inside the service with a mock transport.
    import httpx

    monkeypatch.setattr(settings, "NVIDIA_API_KEY", "fake-key")
    transport = _nvidia_transport("1. Alpha\n2. Beta\n")

    orig_init = httpx.AsyncClient.__init__

    def fake_init(self, *args, **kwargs):
        kwargs.pop("transport", None)
        kwargs.pop("base_url", None)
        return orig_init(
            self, transport=transport, base_url="http://test"
        )

    monkeypatch.setattr(httpx.AsyncClient, "__init__", fake_init)

    candidate = await register_and_login(client, candidate_payload)
    recruiter = await register_and_login(client, recruiter_payload)
    job = await client.post(
        "/api/v1/jobs", json=JOB_PAYLOAD, headers=recruiter["headers"]
    )
    job_id = job.json()["id"]

    response = await client.post(
        "/api/v1/questions/generate",
        json={"job_id": job_id},
        headers=candidate["headers"],
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert [q["text"] for q in body["questions"]] == ["Alpha", "Beta"]


@pytest.fixture
def fake_model_text() -> str:
    return "1. First question\n2. Second question\n3. Third question\n"
