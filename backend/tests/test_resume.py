from __future__ import annotations

from app.services.resume import parse_profile_fields
from tests.conftest import register_and_login

VALID_PDF = b"%PDF-1.4 fake pdf content for testing resume upload"
TOO_BIG = b"x" * (26 * 1024 * 1024)


async def _auth(client, payload):
    return await register_and_login(client, payload)


async def test_candidate_can_upload_resume(client, candidate_payload):
    auth = await _auth(client, candidate_payload)
    resp = await client.post(
        "/api/v1/resume/upload",
        headers=auth["headers"],
        files={"file": ("resume.pdf", VALID_PDF, "application/pdf")},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["filename"] == "resume.pdf"
    assert body["content_type"] == "application/pdf"
    assert body["size_bytes"] == len(VALID_PDF)


async def test_get_resume_metadata(client, candidate_payload):
    auth = await _auth(client, candidate_payload)
    await client.post(
        "/api/v1/resume/upload",
        headers=auth["headers"],
        files={"file": ("resume.pdf", VALID_PDF, "application/pdf")},
    )
    resp = await client.get("/api/v1/resume", headers=auth["headers"])
    assert resp.status_code == 200, resp.text
    assert resp.json()["filename"] == "resume.pdf"


async def test_upload_replaces_existing_resume(client, candidate_payload):
    auth = await _auth(client, candidate_payload)
    first = await client.post(
        "/api/v1/resume/upload",
        headers=auth["headers"],
        files={"file": ("first.pdf", VALID_PDF, "application/pdf")},
    )
    second = await client.post(
        "/api/v1/resume/upload",
        headers=auth["headers"],
        files={"file": ("second.pdf", VALID_PDF, "application/pdf")},
    )
    assert first.json()["id"] != second.json()["id"]
    assert second.json()["filename"] == "second.pdf"


async def test_download_resume(client, candidate_payload):
    auth = await _auth(client, candidate_payload)
    await client.post(
        "/api/v1/resume/upload",
        headers=auth["headers"],
        files={"file": ("resume.pdf", VALID_PDF, "application/pdf")},
    )
    resp = await client.get("/api/v1/resume/download", headers=auth["headers"])
    assert resp.status_code == 200, resp.text
    assert resp.content == VALID_PDF


async def test_delete_resume(client, candidate_payload):
    auth = await _auth(client, candidate_payload)
    await client.post(
        "/api/v1/resume/upload",
        headers=auth["headers"],
        files={"file": ("resume.pdf", VALID_PDF, "application/pdf")},
    )
    resp = await client.delete("/api/v1/resume", headers=auth["headers"])
    assert resp.status_code == 200, resp.text
    after = await client.get("/api/v1/resume", headers=auth["headers"])
    assert after.status_code == 404


async def test_get_resume_when_none_uploaded(client, candidate_payload):
    auth = await _auth(client, candidate_payload)
    resp = await client.get("/api/v1/resume", headers=auth["headers"])
    assert resp.status_code == 404


async def test_reject_unsupported_type(client, candidate_payload):
    auth = await _auth(client, candidate_payload)
    resp = await client.post(
        "/api/v1/resume/upload",
        headers=auth["headers"],
        files={"file": ("resume.txt", b"plain text", "text/plain")},
    )
    assert resp.status_code == 400


async def test_reject_oversized_file(client, candidate_payload):
    auth = await _auth(client, candidate_payload)
    resp = await client.post(
        "/api/v1/resume/upload",
        headers=auth["headers"],
        files={"file": ("big.pdf", TOO_BIG, "application/pdf")},
    )
    assert resp.status_code == 400


async def test_recruiter_cannot_upload_resume(client, recruiter_payload):
    auth = await _auth(client, recruiter_payload)
    resp = await client.post(
        "/api/v1/resume/upload",
        headers=auth["headers"],
        files={"file": ("resume.pdf", VALID_PDF, "application/pdf")},
    )
    assert resp.status_code == 403


async def test_unauthenticated_cannot_upload(client):
    resp = await client.post(
        "/api/v1/resume/upload",
        files={"file": ("resume.pdf", VALID_PDF, "application/pdf")},
    )
    assert resp.status_code == 401


async def test_upload_stores_bytes_in_db(client, candidate_payload):
    auth = await _auth(client, candidate_payload)
    resp = await client.post(
        "/api/v1/resume/upload",
        headers=auth["headers"],
        files={"file": ("resume.pdf", VALID_PDF, "application/pdf")},
    )
    assert resp.status_code == 200

    download = await client.get(
        "/api/v1/resume/download", headers=auth["headers"]
    )
    assert download.status_code == 200
    assert download.content == VALID_PDF


async def test_parse_returns_404_when_no_resume(client, candidate_payload):
    auth = await _auth(client, candidate_payload)
    resp = await client.post("/api/v1/resume/parse", headers=auth["headers"])
    assert resp.status_code == 404


async def test_parse_extracts_and_applies_fields(client, candidate_payload, monkeypatch):
    auth = await _auth(client, candidate_payload)
    await client.post(
        "/api/v1/resume/upload",
        headers=auth["headers"],
        files={"file": ("resume.pdf", VALID_PDF, "application/pdf")},
    )

    sample_text = (
        "Jane Doe\n"
        "github.com/janedoe\n"
        "linkedin.com/in/janedoe\n"
        "Phone: +1 415 555 0199\n"
        "Studied at Stanford University\n"
        "Experienced backend engineer with Python and FastAPI."
    )

    from app.services.resume import ResumeService

    def fake_extract(self, resume):  # noqa: ANN001
        return sample_text

    monkeypatch.setattr(ResumeService, "extract_text", fake_extract)

    resp = await client.post("/api/v1/resume/parse", headers=auth["headers"])
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["parsed_text"] == sample_text
    fields = body["parsed_fields"]
    assert fields["github_url"] == "github.com/janedoe"
    assert fields["linkedin_url"] == "linkedin.com/in/janedoe"
    assert "+1 415 555 0199" in fields["phone"]
    assert "Stanford University" in fields["college"]
    assert fields["bio"]

    profile = await client.get("/api/v1/profile", headers=auth["headers"])
    prof = profile.json()
    assert prof["github_url"] == "github.com/janedoe"
    assert prof["linkedin_url"] == "linkedin.com/in/janedoe"
    assert prof["phone"] == fields["phone"]
    assert "Stanford University" in (prof["college"] or "")
    assert prof["bio"] == sample_text


async def test_parse_does_not_overwrite_existing_profile(client, candidate_payload, monkeypatch):
    auth = await _auth(client, candidate_payload)
    await client.post(
        "/api/v1/resume/upload",
        headers=auth["headers"],
        files={"file": ("resume.pdf", VALID_PDF, "application/pdf")},
    )

    await client.put(
        "/api/v1/profile",
        headers=auth["headers"],
        json={"phone": "+9 999 999 9999", "college": "Existing College"},
    )

    sample_text = (
        "github.com/newuser\n"
        "linkedin.com/in/newuser\n"
        "Phone: +1 415 555 0199\n"
        "Studied at New University\n"
    )

    from app.services.resume import ResumeService

    def fake_extract(self, resume):  # noqa: ANN001
        return sample_text

    monkeypatch.setattr(ResumeService, "extract_text", fake_extract)

    resp = await client.post("/api/v1/resume/parse", headers=auth["headers"])
    assert resp.status_code == 200, resp.text

    profile = await client.get("/api/v1/profile", headers=auth["headers"])
    prof = profile.json()
    assert prof["phone"] == "+9 999 999 9999"
    assert prof["college"] == "Existing College"
    assert prof["github_url"] == "github.com/newuser"
    assert prof["linkedin_url"] == "linkedin.com/in/newuser"


def test_parse_profile_fields_unit():
    text = (
        "John Smith\n"
        "github.com/jsmith\n"
        "linkedin.com/in/jsmith\n"
        "Tel: +44 20 7946 0958\n"
        "Graduate of MIT Institute of Technology\n"
        "Software engineer passionate about distributed systems."
    )
    fields = parse_profile_fields(text)
    assert fields["github_url"] == "github.com/jsmith"
    assert fields["linkedin_url"] == "linkedin.com/in/jsmith"
    assert "+44 20 7946 0958" in fields["phone"]
    assert "MIT Institute of Technology" in fields["college"]
    assert fields["bio"]


def test_parse_profile_fields_no_signals():
    fields = parse_profile_fields("")
    assert all(value is None for value in fields.values())


def test_parse_profile_fields_short_phone_ignored():
    fields = parse_profile_fields("call me at 123")
    assert fields["phone"] is None
