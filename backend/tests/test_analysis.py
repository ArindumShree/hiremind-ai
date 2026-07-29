from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from app.models.interview import Interview
from app.schemas.analysis import Evaluation
from app.services import speech as speech_module
from app.services.evaluation import EvaluationService, compute_evaluation
from app.services.speech import SpeechAnalysisService, compute_metrics
from app.services.video import compute_metrics as compute_video_metrics
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


async def _setup_interview_with_media(
    client: AsyncClient,
) -> tuple[dict, dict, dict]:
    recruiter = await register_and_login(client, _recruiter_payload())
    candidate = await register_and_login(client, _candidate_payload())

    job = await client.post(
        "/api/v1/jobs", json=JOB_PAYLOAD, headers=recruiter["headers"]
    )
    job = job.json()
    await client.patch(
        f"/api/v1/jobs/{job['id']}/publish", headers=recruiter["headers"]
    )
    application = await client.post(
        f"/api/v1/jobs/{job['id']}/apply",
        json={"cover_letter": "Hi"},
        headers=candidate["headers"],
    )
    application = application.json()
    await client.patch(
        f"/api/v1/applications/{application['id']}/status",
        json={"status": "shortlisted"},
        headers=recruiter["headers"],
    )
    start = await client.post(
        "/api/v1/interviews",
        json={"application_id": application["id"]},
        headers=recruiter["headers"],
    )
    interview = start.json()

    import json

    answers = {
        "answers": [
            {"question_id": interview["questions"][0]["id"], "text": "Hello"}
        ]
    }
    files = {
        "answers": (None, json.dumps(answers)),
        "file": ("answer.mp3", b"fake-audio-bytes", "audio/mpeg"),
    }
    await client.post(
        f"/api/v1/interviews/{interview['id']}/submit/media",
        files=files,
        headers=candidate["headers"],
    )
    return recruiter, candidate, interview


# --- Pure metric computation -------------------------------------------------


def test_compute_speech_metrics_counts_fillers() -> None:
    transcript = "um I think uh this is basically a good like answer"
    metrics = compute_metrics(transcript, duration_seconds=6.0)
    assert metrics.word_count > 0
    assert metrics.filler_word_count >= 3
    assert metrics.words_per_minute is not None
    assert 0.0 <= metrics.fluency_score <= 1.0
    assert 0.0 <= metrics.confidence_score <= 1.0


def test_compute_speech_metrics_empty() -> None:
    metrics = compute_metrics("")
    assert metrics.word_count == 0
    assert metrics.fluency_score == 0.0


def test_compute_video_metrics() -> None:
    metrics = compute_video_metrics(10, 8, [1.0] * 8)
    assert metrics.frames_sampled == 10
    assert metrics.frames_with_face == 8
    assert metrics.face_detection_ratio == 0.8
    assert 0.0 <= metrics.engagement_score <= 1.0


def test_compute_video_metrics_zero() -> None:
    metrics = compute_video_metrics(0, 0, [])
    assert metrics.frames_sampled == 0
    assert metrics.engagement_score == 0.0


# --- Speech transcription (Whisper mocked, no download) ----------------------


def test_transcribe_mocks_whisper(monkeypatch, tmp_path) -> None:
    audio = tmp_path / "answer.wav"
    audio.write_bytes(b"fake")

    class _FakeModel:
        def transcribe(self, path):  # noqa: ANN001
            return {"text": "  hello world  "}

    class _FakeWhisper:
        @staticmethod
        def load_model(name):  # noqa: ANN001
            return _FakeModel()

    import sys

    monkeypatch.setitem(sys.modules, "whisper", _FakeWhisper)
    result = SpeechAnalysisService().transcribe(str(audio))
    assert result == "hello world"


def test_transcribe_missing_file() -> None:
    from app.core.errors import BadRequestError

    with pytest.raises(BadRequestError):
        SpeechAnalysisService().transcribe("nonexistent-file.wav")


def test_analyze_uses_transcribe(monkeypatch, tmp_path) -> None:
    audio = tmp_path / "a.wav"
    audio.write_bytes(b"fake")
    monkeypatch.setattr(
        speech_module.SpeechAnalysisService,
        "transcribe",
        lambda self, path: "um this is a test answer",
    )
    metrics = SpeechAnalysisService().analyze(str(audio))
    assert metrics.transcript == "um this is a test answer"
    assert metrics.word_count > 0


# --- Evaluation combines + degrades without Gemini ---------------------------


def test_compute_evaluation_combines_metrics() -> None:
    interview = Interview(
        application_id=uuid.uuid4(),
        questions_json=[{"id": "0", "text": "a" * 200}],
        speech_metrics={"fluency_score": 0.8, "confidence_score": 0.7},
        video_metrics={"engagement_score": 0.6, "eye_contact_score": 0.5},
    )
    evaluation = compute_evaluation(interview)
    assert 0.0 <= evaluation.overall_score <= 100.0
    assert len(evaluation.dimensions) == 3
    assert evaluation.summary


@pytest.mark.asyncio
async def test_evaluation_degrades_without_gemini(monkeypatch) -> None:
    from app.config.settings import settings

    monkeypatch.setattr(settings, "NVIDIA_API_KEY", "")
    interview = Interview(
        application_id=uuid.uuid4(),
        questions_json=[{"id": "0", "text": "answer"}],
        speech_metrics={"fluency_score": 0.5, "confidence_score": 0.5},
        video_metrics={"engagement_score": 0.5, "eye_contact_score": 0.5},
    )
    evaluation = await EvaluationService().evaluate(interview)
    assert isinstance(evaluation, Evaluation)
    assert evaluation.ai_feedback is None


# --- Endpoints: store results + ownership guards -----------------------------


async def test_speech_endpoint_stores_results(client: AsyncClient, monkeypatch) -> None:
    monkeypatch.setattr(
        speech_module.SpeechAnalysisService,
        "transcribe",
        lambda self, path: "um hello this is my recorded answer for the role",
    )
    _, candidate, interview = await _setup_interview_with_media(client)
    response = await client.post(
        f"/api/v1/interviews/{interview['id']}/speech-analysis",
        headers=candidate["headers"],
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["word_count"] > 0
    assert "transcript" in body


async def test_evaluate_endpoint_stores_results(client: AsyncClient, monkeypatch) -> None:
    import httpx

    monkeypatch.setattr(
        speech_module.SpeechAnalysisService,
        "transcribe",
        lambda self, path: "hello this is my answer",
    )
    # Avoid a real network call to NVIDIA for the optional AI feedback.
    transport = httpx.MockTransport(
        lambda req: httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"role": "assistant", "content": "Solid candidate."}}
                ]
            },
        )
    )
    orig_init = httpx.AsyncClient.__init__

    def fake_init(self, *args, **kwargs):
        kwargs.pop("transport", None)
        kwargs.pop("base_url", None)
        return orig_init(self, transport=transport, base_url="http://test")

    monkeypatch.setattr(httpx.AsyncClient, "__init__", fake_init)

    recruiter, candidate, interview = await _setup_interview_with_media(client)
    await client.post(
        f"/api/v1/interviews/{interview['id']}/speech-analysis",
        headers=candidate["headers"],
    )
    response = await client.post(
        f"/api/v1/interviews/{interview['id']}/evaluate",
        headers=recruiter["headers"],
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert 0.0 <= body["overall_score"] <= 100.0
    assert len(body["dimensions"]) == 3


async def test_get_evaluation_endpoint(client: AsyncClient, monkeypatch) -> None:
    import httpx

    transport = httpx.MockTransport(
        lambda req: httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"role": "assistant", "content": "Solid candidate."}}
                ]
            },
        )
    )
    orig_init = httpx.AsyncClient.__init__

    def fake_init(self, *args, **kwargs):
        kwargs.pop("transport", None)
        kwargs.pop("base_url", None)
        return orig_init(self, transport=transport, base_url="http://test")

    monkeypatch.setattr(httpx.AsyncClient, "__init__", fake_init)

    recruiter, _, interview = await _setup_interview_with_media(client)
    response = await client.get(
        f"/api/v1/interviews/{interview['id']}/evaluation",
        headers=recruiter["headers"],
    )
    assert response.status_code == 200, response.text
    assert "overall_score" in response.json()


async def test_speech_analysis_ownership_forbidden(client: AsyncClient) -> None:
    _, _, interview = await _setup_interview_with_media(client)
    intruder = await register_and_login(
        client,
        {
            "full_name": "Other Candidate",
            "email": "other@example.com",
            "password": "StrongPass1",
            "confirm_password": "StrongPass1",
            "role": "candidate",
        },
    )
    response = await client.post(
        f"/api/v1/interviews/{interview['id']}/speech-analysis",
        headers=intruder["headers"],
    )
    assert response.status_code == 404


async def test_evaluation_missing_interview_404(client: AsyncClient) -> None:
    recruiter = await register_and_login(client, _recruiter_payload())
    response = await client.get(
        f"/api/v1/interviews/{uuid.uuid4()}/evaluation",
        headers=recruiter["headers"],
    )
    assert response.status_code == 404
