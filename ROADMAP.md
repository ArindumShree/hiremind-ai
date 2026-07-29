# ROADMAP.md

Complete product roadmap for HireMind AI. Each sprint represents one
development session. Status values: **Not Started**, **In Progress**,
**Completed**.

===============================================================================

## Sprint 1 — Project Foundation
**Status:** Completed (2026-07-18)
- [x] Scaffold frontend (Vite + React + TS + Tailwind + Router + TanStack Query + ESLint/Prettier).
- [x] Scaffold backend (FastAPI + SQLAlchemy async + Alembic).
- [x] Docker Compose for local dev (PostgreSQL + backend + frontend).
- [x] Environment configuration and `.env.example` (backend, frontend, docker).
- [x] Centralized logging and error-handling skeleton.
- [x] Health endpoint (`/api/v1/health`) with DB probe.
- [x] Base CI (`.github/workflows/ci.yml`).
- [!] Live `docker compose up` deferred (Docker daemon needs WSL2/Hyper-V +
     admin UAC, unavailable in this headless env). `docker compose config`
     validated; real PostgreSQL connection VERIFIED separately.

## Sprint 2 — Authentication
**Status:** Completed (2026-07-18)
- User registration and login (Candidate + Recruiter roles).
- JWT-based auth (access + refresh tokens, HS256).
- Password hashing (argon2).
- Protected route / dependency middleware (backend `require_role`, frontend guards).
- Refresh-token rotation + revocation on logout; user profile GET/PUT.

## Sprint 3 — Hiring Domain (Job + Application)
**Status:** Completed (2026-07-19)
- Job entity (soft-delete) + Application entity (unique candidate/job) with
  enums (EmploymentType, JobStatus, ApplicationStatus).
- Backend: models, schemas, repositories, services, REST APIs (job CRUD +
  publish/close, apply / list-applicants / my-applications / status update),
  Alembic migration, RBAC + pagination/search/filter.
- Frontend: job service, reusable components (badges/cards/table/form), and
  pages (recruiter job management, candidate browse/apply, applicant review)
  wired with role-guarded routes.
- Note: Candidate/Recruiter profile extensions and Interview/Evaluation
  entities are deferred to later sprints (no AI/resume/interview work yet).

## Sprint 4 — Resume Upload
**Status:** Completed (2026-07-19)
- File upload endpoint (multipart) + local storage under `uploads/candidates/<id>`.
- Validation: PDF/DOC/DOCX, content-type check, <= 25 MB.
- One resume per candidate (re-upload replaces the prior file); download/delete.
- Candidate-only REST API (`/resume`, `/resume/upload`, `/resume/download`,
  DELETE `/resume`) + Alembic migration; frontend ResumeManager + `/resume` page.
- Note: this is the second half of the original Sprint 3, split out when that
  sprint was paused. The Job + Application half is Sprint 3 (Completed).

## Sprint 5 — Resume Parsing
**Status:** Completed (2026-07-19)
- Extract text from PDF/DOCX (pdfplumber + python-docx; DOC errors gracefully).
- Structured parsing into candidate profile fields (github/linkedin URLs,
  phone, college keyword, bio) with conservative no-overwrite merge.
- POST `/resume/parse` (candidate-only) writes parsed fields to the profile;
  `ResumeParsed` schema; tests cover 404/extraction/apply/no-overwrite.

## Sprint 6 — AI Question Generation
**Status:** Completed (2026-07-19)
- NVIDIA API integration (`httpx` -> `integrate.api.nvidia.com/v1`,
  key from `NVIDIA_API_KEY` env; graceful 400 when unset) for role-based
  questions. Model: `nvidia/llama-3.3-nemotron-super-49b-v1`.
- Prompt templates per job/position (`build_prompt`: generic +
  engineer/designer role-aware branches); `POST /questions/generate`
  (candidate-only) returns a structured `QuestionList`.
- Tests cover parsing, clean-list, 400 (no key), 404 (missing job), 200.

## Sprint 7 — Interview Module
**Status:** Completed (2026-07-19)
- Interview session lifecycle (start/submit) via `Interview` model (unique FK
  to Application, status enum, JSON questions/answers).
- Question delivery to candidate (GET `/interviews/{id}`).
- Answer capture (text inline + audio/video file storage under
  `uploads/interviews/<id>/`); Application status transitions
  (interview_scheduled -> interview_completed). Alembic migration + tests.

## Sprint 8 — Speech Analysis
**Status:** Completed (2026-07-19)
- Whisper transcription of interview audio.
- Speech metrics (fluency, clarity).

## Sprint 9 — Video Analysis
**Status:** Completed (2026-07-19)
- MediaPipe + OpenCV for posture/eye-contact signals.
- Non-invasive, privacy-respecting heuristics.

## Sprint 10 — Evaluation Engine
**Status:** Completed (2026-07-19)
- Combine answers + speech + video into score.
- Gemini-based qualitative feedback.
- Store evaluation results.

## Sprint 11 — Recruiter Dashboard
**Status:** Completed (2026-07-19)
- View candidates and applications (`GET /candidates`, ownership-enforced).
- Compare applicants side by side (`POST /candidates/compare`).
- Review AI evaluations, download reports (JSON; PDF fallback if reportlab).

## Sprint 12 — Deployment
**Status:** Completed (2026-07-19)
- Production Docker images (backend python:3.12-slim non-root + alembic on
  start; frontend node:20 build -> nginx:1.27 serving `/api` proxy).
- Compose/orchestration for staging (`db` postgres:17-alpine ->
  `backend` -> `frontend`, healthchecks, depends_on).
- Basic observability (`/health` DB check + JSON logging) and secrets
  management (all via gitignored `backend/.env`; required secrets documented
  in `docker/docker-compose.env.example`).

===============================================================================
