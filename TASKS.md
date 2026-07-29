# TASKS.md

Work tracking for the current sprint. Use checkboxes. When a sprint completes,
archive its tasks and create the next sprint's list.

===============================================================================

## Stage 1 — Project Foundation (Completed)

### Frontend
- [x] Initialize Vite + React + TypeScript project
- [x] Configure TailwindCSS
- [x] Set up base folder structure (components, pages, services, hooks)
- [x] Add base layout / theme
- [x] Add React Router + TanStack Query + Axios
- [x] Add ESLint + Prettier

### Backend
- [x] Initialize FastAPI application skeleton (app factory)
- [x] Configure SQLAlchemy + async engine
- [x] Set up Alembic (no migrations yet)
- [x] Add core config (env loading, settings)
- [x] Add centralized logging
- [x] Add centralized error-handling middleware + error envelope
- [x] Health-check endpoint (with DB probe)

### Infrastructure
- [x] Docker Compose (PostgreSQL + backend + frontend)
- [x] Dockerfile (backend, frontend + nginx)
- [x] `.env.example` for backend and frontend
- [x] Base CI workflow
- [x] README + docs

### Verification
- [x] Backend builds / runs (uvicorn starts, health responds)
- [x] Frontend builds / runs (npm build + lint pass)
- [x] Tests pass (pytest 1 passed) + ruff clean
- [x] Live PostgreSQL connection VERIFIED (health `database: ok`, pytest vs live DB)
- [x] `docker compose config` validated (3 services, env_file, healthcheck)
- [!] Live `docker compose up` run — pending admin-enabled Docker daemon (WSL2/Hyper-V)

===============================================================================

## Stage 2 — Authentication (Completed)

### Backend
- [x] User model + Profile + RefreshToken models (UUID PKs via portable GUID type)
- [x] Alembic migration `78b2ad2e40bb` (users, profiles, refresh_tokens tables)
- [x] Password hashing (argon2 via passlib)
- [x] Registration endpoint (Candidate + Recruiter roles) + password strength/match rules
- [x] Login endpoint returning JWT access + refresh tokens (HS256)
- [x] Token refresh endpoint (rotation + jti-based revocation)
- [x] JWT auth dependency / protected route (`get_current_user`, `require_role` factory)
- [x] Logout endpoint (revokes refresh token)
- [x] `/auth/me` + `/profile` GET/PUT endpoints
- [x] User/profile/refresh_token schemas, repositories, services
- [x] Fixed CORS list parse (NoDecode) + validation-error serialization (jsonable_encoder)

### Frontend
- [x] Auth types (`src/types/index.ts`)
- [x] API client with Bearer interceptor + 401 refresh-rotation (`src/services/api.ts`)
- [x] AuthContext provider (login/register/logout, current user) (`src/context/`)
- [x] Login / Register real forms (were placeholders)
- [x] Token storage (localStorage) + Axios interceptor
- [x] Protected route wrapper + role guards (`src/routes/ProtectedRoute.tsx`)
- [x] Auth-aware Layout nav; role-aware Dashboard

### Verification
- [x] Backend auth tests: 18 new (auth/profile/rbac) + 1 health = 20 passed; ruff clean
- [x] Live end-to-end flow vs PostgreSQL verified (register/login/me/refresh/logout/profile)
- [x] Frontend `npm run build` (tsc + vite) passes
- [x] Frontend `npm run lint` clean (0 warnings)
- [!] Live `docker compose up` still pending admin-enabled Docker daemon

===============================================================================

## Archive

### (None prior to Stage 1)

===============================================================================

## Stage 3 — Hiring Domain (Completed, 2026-07-19)

> Renamed from "Database Models": implemented Job + Application domain
> end-to-end (models, schemas, repos, services, APIs, migration, tests)
> plus the recruiter/candidate frontend. No AI/resume/interview features.

### Backend
- [x] Enums extended: `EmploymentType`, `JobStatus` (draft/published/closed/archived),
      `ApplicationStatus` (applied/shortlisted/interview_scheduled/
      interview_completed/rejected/hired) in `app/models/enums.py`
- [x] `Job` model (soft-delete `is_deleted`/`deleted_at`, FK `posted_by` -> users)
- [x] `Application` model (FK candidate/job, unique `(candidate_id, job_id)`)
- [x] User relationships (jobs, applications) wired
- [x] Schemas: `job.py` (Base/Create/Update/Read/ListParams), `application.py`
      (Create/StatusUpdate/Read w/ nested candidate), `pagination.py`
      (`PageMeta` + `PaginatedResponse[T]` PEP695 generic)
- [x] Repos: `job.py` (list_by_recruiter, list_published w/ filters+pagination,
      get_owned_by_id, soft_delete), `application.py`
- [x] Services: `job.py` `JobService` + `ApplicationService` (only published jobs
      accept applications; dup prevention; ownership checks)
- [x] APIs: `job.py` (CRUD + publish/close), `application.py`
      (apply / list-applicants / my-applications / status update), `deps.py`
      (`parse_job_id` dependency); wired into `main.py`
- [x] Alembic migration `3a7f1c9d2e4_jobs_and_applications.py` (jobs +
      applications, FKs, unique constraint, indexes); validated offline `--sql`

### Frontend
- [x] Types `src/types/index.ts`: Job, Application, enums, PageMeta,
      PaginatedJobs, `*_TEXT` label maps
- [x] Service `src/services/jobs.ts` (create/listMine/browse/get/update/remove/
      publish/close/apply/listApplicants/myApplications)
- [x] Components: JobStatusBadge, ApplicationStatusBadge, JobCard, JobTable,
      JobForm, Loading, ErrorMessage
- [x] Pages: RecruiterJobList, CreateJob, EditJob, ViewApplicants, BrowseJobs,
      JobDetails, AppliedJobs; wired into `App.tsx` (role-guarded routes) +
      Layout nav + role-aware dashboards
- [x] Fixed `tsc` parse bug: inline `as { response?: {...} }` assertion triggered
      a phantom TS1005; replaced with named `ApiErrorShape` interface in all
      `extractError` helpers. Also fixed component `../../types` -> `../types`
      import paths.

### Verification
- [x] Backend: 38 pytest passed (18 new job/application tests), ruff clean
- [x] Frontend `npm run build` (tsc + vite) passes
- [x] Frontend `npm run lint` clean (0 warnings)
- [!] Live `docker compose up` still pending admin-enabled Docker daemon
- [!] Live PostgreSQL verification still blocked this session (portable PG killed
      when shell exits); used SQLite in-memory test suite + offline Alembic SQL.

===============================================================================

## Sprint 4 — Resume Upload (Completed, 2026-07-19)

### Backend
- [x] `Resume` model (`app/models/resume.py`): one-per-candidate (unique
      `candidate_id`, FK -> users cascade), stores filename/stored_path/
      content_type/size_bytes/created_at
- [x] `ResumeRead` schema; `ResumeRepository`; `ResumeService` (validation:
      PDF/DOC/DOCX + content-type + <=25MB; upsert replaces prior file and
      deletes old file from disk; download/delete)
- [x] API `app/api/resume.py` (router `/resume`): POST `/upload`
      (multipart, candidate-only), GET `` (metadata), GET `/download`
      (FileResponse), DELETE `` ; wired into `main.py`
- [x] Alembic migration `4b1c2d3e5f6_resumes.py` (resumes table + unique
      constraint + index); validated offline `--sql`
- [x] Tests: `tests/test_resume.py` (11 tests: upload/get/replace/download/
      delete/404/type+size rejection/recruiter-403/unauth-401/disk-write)

### Frontend
- [x] `Resume` type in `src/types/index.ts`
- [x] `src/services/resume.ts` (get/upload/download/remove; multipart FormData)
- [x] `src/components/ResumeManager.tsx` (upload/replace/download/remove UI)
- [x] `src/pages/ResumePage.tsx` + route `/resume` (candidate-guarded) +
      Layout nav link + CandidateDashboard card

### Verification
- [x] Backend: 49 pytest passed (11 new resume tests), ruff clean
- [x] Frontend `npm run build` (tsc + vite) passes
- [x] Frontend `npm run lint` clean (0 warnings)
- [!] Live `docker compose up` / PostgreSQL verification still blocked (same as
      Sprint 3). Added `uploads/` to `.gitignore`.
