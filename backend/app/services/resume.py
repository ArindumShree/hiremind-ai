from __future__ import annotations

import io
import mimetypes
import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.errors import BadRequestError, NotFoundError
from app.models.resume import Resume
from app.repositories.resume import ResumeRepository

MAX_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

BIO_MAX_LENGTH = 2000

_GITHUB_RE = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+", re.IGNORECASE
)
_LINKEDIN_RE = re.compile(
    r"(?:https?://)?(?:www\.)?linkedin\.com/(?:in|pub)/[A-Za-z0-9_-]+",
    re.IGNORECASE,
)
_PHONE_RE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
_COLLEGE_KEYWORDS = (
    "university",
    "college",
    "institute",
    "instituto",
    "academy",
    "school of",
    "polytechnic",
)

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


class ResumeService:
    """Business logic for uploading, fetching and removing candidate resumes."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._resumes = ResumeRepository(session)

    async def get_for_candidate(self, candidate_id: uuid.UUID) -> Resume | None:
        return await self._resumes.get_by_candidate_id(candidate_id)

    async def upload(
        self,
        candidate_id: uuid.UUID,
        filename: str,
        content_type: str,
        data: bytes,
    ) -> Resume:
        """Validate, persist and register a candidate's resume file."""
        self._validate(filename, content_type, data)

        existing = await self._resumes.get_by_candidate_id(candidate_id)
        if existing is not None:
            await self._resumes.delete_by_candidate_id(candidate_id)
            await self._session.flush()

        resume = Resume(
            candidate_id=candidate_id,
            filename=filename,
            stored_path="db://resumes/" + str(candidate_id),
            content_type=content_type,
            size_bytes=len(data),
            file_data=data,
        )
        resume = await self._resumes.add(resume)
        await self._session.commit()
        await self._session.refresh(resume)
        return resume

    async def delete_for_candidate(self, candidate_id: uuid.UUID) -> None:
        resume = await self._resumes.get_by_candidate_id(candidate_id)
        if resume is None:
            return
        await self._resumes.delete_by_candidate_id(candidate_id)
        await self._session.commit()

    def _validate(self, filename: str, content_type: str, data: bytes) -> None:
        if not filename:
            raise BadRequestError("Missing file name")
        extension = os.path.splitext(filename)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise BadRequestError(
                "Unsupported file type. Allowed: PDF, DOC, DOCX."
            )
        if content_type not in ALLOWED_CONTENT_TYPES:
            detected = mimetypes.guess_type(filename)[0]
            if detected not in ALLOWED_CONTENT_TYPES:
                raise BadRequestError("Unsupported file content type.")
        if len(data) == 0:
            raise BadRequestError("Uploaded file is empty.")
        if len(data) > MAX_SIZE_BYTES:
            raise BadRequestError(
                f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB} MB limit."
            )

    def extract_text(self, resume: Resume) -> str:
        """Extract plain text from a stored resume file.

        PDF and DOCX are fully supported. Legacy ``.doc`` files raise a
        clear :class:`BadRequestError` since reliable parsing requires
        external tools that are not guaranteed to be available.
        """
        data = resume.file_data
        if not data:
            raise BadRequestError(
                "Resume file data is missing; please re-upload the resume"
            )

        extension = os.path.splitext(resume.filename)[1].lower()
        content_type = resume.content_type.lower()

        if extension == ".pdf" or content_type == "application/pdf":
            return self._extract_pdf(data)
        if extension == ".docx" or (
            "wordprocessingml" in content_type or "officedocument" in content_type
        ):
            return self._extract_docx(data)
        if extension == ".doc" or content_type == "application/msword":
            raise BadRequestError(
                "DOC parsing unsupported; please upload PDF or DOCX"
            )
        raise BadRequestError(
            "Unsupported resume format for text extraction"
        )

    @staticmethod
    def _extract_pdf(data: bytes) -> str:
        import pdfplumber

        pages: list[str] = []
        try:
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                for page in pdf.pages:
                    pages.append(page.extract_text() or "")
        except Exception as exc:  # pragma: no cover - depends on file bytes
            raise BadRequestError(f"Failed to read PDF: {exc}") from exc
        return _normalize_whitespace("\n".join(pages))

    @staticmethod
    def _extract_docx(data: bytes) -> str:
        import docx

        try:
            document = docx.Document(io.BytesIO(data))
        except Exception as exc:  # pragma: no cover - depends on file bytes
            raise BadRequestError(f"Failed to read DOCX: {exc}") from exc
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        return _normalize_whitespace("\n".join(paragraphs))

    async def parse_into_profile(
        self, candidate_id: uuid.UUID
    ) -> dict[str, object]:
        """Extract text, parse structured fields and apply them to the profile.

        Returns a dict with ``parsed_text`` and ``parsed_fields``. Only empty
        profile fields are populated; existing values are preserved.
        """
        resume = await self._resumes.get_by_candidate_id(candidate_id)
        if resume is None:
            raise NotFoundError("No resume uploaded yet")

        parsed_text = self.extract_text(resume)
        parsed_fields = parse_profile_fields(parsed_text)

        from app.repositories.profile import ProfileRepository

        profiles = ProfileRepository(self._session)
        profile = await profiles.get_by_user_id(candidate_id)
        if profile is None:
            raise NotFoundError("Profile not found")

        applied: dict[str, object] = {}
        for field, value in parsed_fields.items():
            if value is None:
                continue
            current = getattr(profile, field, None)
            if current in (None, ""):
                setattr(profile, field, value)
                applied[field] = value

        await self._session.commit()
        await self._session.refresh(profile)

        return {"parsed_text": parsed_text, "parsed_fields": parsed_fields}


def _normalize_whitespace(text: str) -> str:
    """Collapse runs of whitespace and trim the resulting text."""
    return re.sub(r"\s+", " ", text).strip()


def parse_profile_fields(text: str) -> dict[str, object]:
    """Scan resume text and extract a conservative set of profile fields.

    Only confident signals populate a field. ``bio`` is filled with remaining
    meaningful text when present.
    """
    fields: dict[str, object] = {
        "github_url": None,
        "linkedin_url": None,
        "phone": None,
        "college": None,
        "bio": None,
    }

    github_match = _GITHUB_RE.search(text)
    if github_match:
        fields["github_url"] = github_match.group(0).rstrip("/")

    linkedin_match = _LINKEDIN_RE.search(text)
    if linkedin_match:
        fields["linkedin_url"] = linkedin_match.group(0).rstrip("/")

    phone_match = _PHONE_RE.search(text)
    if phone_match:
        phone = phone_match.group(0).strip()
        if len(re.sub(r"\D", "", phone)) >= 7:
            fields["phone"] = phone

    college = _find_college(text)
    if college:
        fields["college"] = college

    if text:
        fields["bio"] = text[:BIO_MAX_LENGTH]

    return fields


def _find_college(text: str) -> str | None:
    lowered = text.lower()
    for keyword in _COLLEGE_KEYWORDS:
        index = lowered.find(keyword)
        if index == -1:
            continue
        start = text.rfind("\n", 0, index)
        if start == -1:
            start = 0
        else:
            start += 1
        end = text.find("\n", index)
        if end == -1:
            end = len(text)
        snippet = text[start:end].strip()
        if len(snippet) > 150:
            snippet = snippet[:150]
        return snippet
    return None
