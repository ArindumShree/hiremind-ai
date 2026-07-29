from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import BadRequestError, NotFoundError
from app.models.application import Application
from app.models.enums import ApplicationStatus, JobStatus
from app.models.job import Job
from app.repositories.application import ApplicationRepository
from app.repositories.interview import InterviewRepository
from app.repositories.job import JobRepository
from app.schemas.application import ApplicationRead
from app.schemas.job import JobCreate, JobUpdate
from app.schemas.pagination import PageMeta
from app.utils.time import utc_now


class JobService:
    """Business logic for recruiters managing job postings."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._jobs = JobRepository(session)

    async def create(self, recruiter_id: uuid.UUID, payload: JobCreate) -> Job:
        job = Job(posted_by=recruiter_id, **payload.model_dump())
        await self._jobs.add(job)
        await self._session.commit()
        await self._session.refresh(job)
        return job

    async def get_owned(self, job_id: uuid.UUID, recruiter_id: uuid.UUID) -> Job:
        job = await self._jobs.get_owned_by_id(job_id, recruiter_id)
        if job is None:
            raise NotFoundError("Job not found")
        return job

    async def update(
        self, job_id: uuid.UUID, recruiter_id: uuid.UUID, payload: JobUpdate
    ) -> Job:
        job = await self.get_owned(job_id, recruiter_id)
        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(job, field, value)
        await self._session.commit()
        await self._session.refresh(job)
        return job

    async def delete(self, job_id: uuid.UUID, recruiter_id: uuid.UUID) -> None:
        job = await self.get_owned(job_id, recruiter_id)
        # Soft delete: preserve historical applications / hiring data.
        job.is_deleted = True
        job.deleted_at = utc_now()
        await self._session.commit()

    async def publish(self, job_id: uuid.UUID, recruiter_id: uuid.UUID) -> Job:
        job = await self.get_owned(job_id, recruiter_id)
        job.status = JobStatus.PUBLISHED
        await self._session.commit()
        await self._session.refresh(job)
        return job

    async def close(self, job_id: uuid.UUID, recruiter_id: uuid.UUID) -> Job:
        job = await self.get_owned(job_id, recruiter_id)
        job.status = JobStatus.CLOSED
        await self._session.commit()
        await self._session.refresh(job)
        return job

    async def list_mine(self, recruiter_id: uuid.UUID) -> list[Job]:
        return await self._jobs.list_by_recruiter(recruiter_id)

    async def browse(
        self,
        *,
        search: str | None = None,
        location: str | None = None,
        employment_type: object | None = None,
        status: JobStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Job], PageMeta]:
        items, total = await self._jobs.list_published(
            search=search,
            location=location,
            employment_type=employment_type,
            status=status,
            page=page,
            page_size=page_size,
        )
        total_pages = (total + page_size - 1) // page_size if total else 0
        meta = PageMeta(
            page=page, page_size=page_size, total=total, total_pages=total_pages
        )
        return items, meta


class ApplicationService:
    """Business logic for candidates applying and recruiters triaging."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._applications = ApplicationRepository(session)
        self._jobs = JobRepository(session)
        self._interviews = InterviewRepository(session)

    async def apply(
        self, candidate_id: uuid.UUID, job_id: uuid.UUID, cover_letter: str | None
    ) -> Application:
        job = await self._jobs.get_by_id(job_id)
        if job is None or job.is_deleted:
            raise NotFoundError("Job not found")

        if job.status != JobStatus.PUBLISHED:
            raise BadRequestError("Applications are only open for published jobs")

        if await self._applications.exists_for_user_and_job(candidate_id, job_id):
            raise BadRequestError("You have already applied to this job")

        application = Application(
            candidate_id=candidate_id,
            job_id=job_id,
            cover_letter=cover_letter,
            status=ApplicationStatus.APPLIED,
        )
        await self._applications.add(application)
        await self._session.commit()
        await self._session.refresh(application)
        return application

    async def list_mine(self, candidate_id: uuid.UUID) -> list[ApplicationRead]:
        applications = await self._applications.list_by_candidate(candidate_id)
        return await self._with_interview_id(applications)

    async def list_for_job(
        self, job_id: uuid.UUID, recruiter_id: uuid.UUID
    ) -> list[ApplicationRead]:
        # Ensure the job exists and belongs to the requesting recruiter.
        await JobService(self._session).get_owned(job_id, recruiter_id)
        applications = await self._applications.list_by_job(job_id)
        return await self._with_interview_id(applications)

    async def _with_interview_id(
        self, applications: list[Application]
    ) -> list[ApplicationRead]:
        """Attach the related interview id (if any) to each application."""
        read_list = [ApplicationRead.model_validate(a) for a in applications]
        if not applications:
            return read_list
        interview_map = await self._interviews.get_interview_ids_for_applications(
            [a.id for a in applications]
        )
        for read, application in zip(read_list, applications, strict=False):
            read.interview_id = interview_map.get(application.id)
        return read_list

    async def update_status(
        self,
        application_id: uuid.UUID,
        recruiter_id: uuid.UUID,
        status: ApplicationStatus,
    ) -> Application:
        application = await self._applications.get_by_id(application_id)
        if application is None:
            raise NotFoundError("Application not found")
        # Ownership check via the parent job.
        await JobService(self._session).get_owned(
            application.job_id, recruiter_id
        )
        application.status = status
        await self._session.commit()
        await self._session.refresh(application)
        return application
