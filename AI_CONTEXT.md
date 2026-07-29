# AI_CONTEXT.md

Concise, always-current snapshot of the HireMind AI project for AI assistants.
Update this whenever the project state changes.

===============================================================================

## Current Stage
**Sprint 6 — AI Question Generation COMPLETED, 2026-07-19** (verified
via autonomous 3-agent workflow: coder implemented, reviewer PASS 9/10).
Backend calls NVIDIA's OpenAI-compatible API (`httpx` ->
`integrate.api.nvidia.com/v1`, key from `NVIDIA_API_KEY`, graceful 400
when unset) with role-based prompt templates; `POST /questions/generate`
(candidate-only) returns a structured QuestionList. Live call verified HTTP 200.
Sprint 7 (Interview Module) COMPLETED. Sprint 11 (Recruiter Dashboard)
COMPLETED (candidate list/compare/report, frontend pages). Sprints 8/9/10
(Speech/Video/Evaluation) are ML-dependent and DEFERRED — heavy deps
(Whisper/MediaPipe/Gemini) could not be installed in the headless env.
ALL 12 SPRINTS COMPLETED (2026-07-19). ML deps (openai-whisper,
mediapipe, opencv-python-headless) installed in the backend venv; Sprints
8/9/10 implemented with lazy ML imports + graceful NVIDIA degradation
(evaluation service uses the same NVIDIA endpoint for optional AI feedback).
Sprint 6 NVIDIA key supplied in backend/.env (nvapi-...); live question
generation verified working (HTTP 200). Production Docker
images + compose staging ready.
The autonomous 3-agent workflow (orchestrator/coder/reviewer) drives Sprints
5→12 to completion; it stops only when every sprint in ROADMAP.md is Completed.

## Completed Stages
- Session1/1b: Documentation foundation (MEMORY, ROADMAP, ARCHITECTURE, TASKS,
  README, AGENTS).
- Stage 1: Backend + frontend scaffolding, Docker, logging/errors, health, CI.
- Stage 2: Full authentication (JWT access+refresh, argon2, RBAC, profile).
- Stage 3: Hiring domain — Job + Application entities, APIs, migration, and
  recruiter/candidate frontend.
- Sprint 4: Resume Upload — candidate resume file storage + validation.

## Current Folder Structure
```
hiremind-ai/
├── frontend/      React+Vite+TS+Tailwind
│   ├── src/
│   │   ├── pages/{Home,Login,Register,Dashboard,CandidateDashboard,
│   │   │         RecruiterDashboard,RecruiterJobList,CreateJob,EditJob,
│   │   │         ViewApplicants,BrowseJobs,JobDetails,AppliedJobs,
│   │   │         ResumePage,NotFound}.tsx
│   │   ├── components/{JobCard,JobTable,JobForm,JobStatusBadge,
│   │   │            ApplicationStatusBadge,Loading,ErrorMessage,ResumeManager}.tsx
│   │   ├── layouts/Layout.tsx          # auth-aware nav
│   │   ├── context/{AuthContext,authContextValue}.tsx  # provider + useAuth hook
│   │   ├── routes/ProtectedRoute.tsx   # route guard + role guard
│   │   ├── services/{api,jobs,resume}.ts  # axios interceptor + jobService
│   │   ├── types/index.ts              # User/Job/Application/Resume/enums/*_TEXT
│   │   └── App.tsx
├── backend/
│   ├── app/
│   │   ├── api/{health,auth,profile,job,application,resume,deps}.py
│   │   ├── core/{database,logging,errors,security}.py
│   │   ├── config/settings.py          # pydantic-settings (+ NoDecode CORS fix)
│   │   ├── middleware/{exceptions,logging}.py
│   │   ├── models/{user,profile,refresh_token,job,application,resume,types,enums}.py
│   │   ├── schemas/{auth,user,profile,job,application,pagination,resume}.py
│   │   ├── services/{auth,profile,job,resume}.py
│   │   ├── repositories/{user,profile,refresh_token,job,application,resume}.py
│   │   └── main.py
│   ├── alembic/versions/{78b2ad2e40bb_*,3a7f1c9d2e4_*,4b1c2d3e5f6_*}.py
│   ├── tests/{test_health,test_auth,test_profile,test_rbac,test_jobs,
│   │   │      test_resume,conftest}.py
│   ├── requirements.txt, Dockerfile, .env.example, pyproject.toml
├── docker/docker-compose.env.example
├── docs/README.md
├── .github/workflows/ci.yml
├── docker-compose.yml
└── README.md
```

## Current Tech Stack
- Frontend: React 18, TypeScript, Vite 5, TailwindCSS 3, React Router 6,
  TanStack Query 5, Axios, ESLint 8, Prettier 3.
- Backend: FastAPI (async), Pydantic 2, SQLAlchemy 2.0 (async), Alembic,
  asyncpg + psycopg, python-json-logger, ruff, pytest + pytest-asyncio.
- DB: PostgreSQL 17 (Docker image postgres:17-alpine).
- Deploy: Docker + Docker Compose (python:3.12-slim, node:20-alpine->nginx).

## Architecture Summary
Modular Monolith. Backend layers: `api -> services -> repositories -> models`,
with `core` (config/db/logging/errors) and `middleware` cross-cutting.
Dependency injection via FastAPI `Depends`. Centralized JSON error envelope
(`{error:{code,message,details}, status_code}`). App created via factory in
`app/main.py`; middleware: CORS + request-logging. Health endpoint probes DB
with a 3s timeout. Frontend uses QueryClient + Axios; dev proxies `/api` to
backend:8000; Docker nginx proxies `/api/` to `backend:8000`.

## Current Development Status
- Backend: auth + hiring domain + resume upload implemented. `pytest` 49 passed
  (auth/profile/rbac/health/jobs/resume); `ruff check` clean. Job + Application
  + Resume models/schemas/repos/services/APIs + Alembic migrations
  (`3a7f1c9d2e4`, `4b1c2d3e5f6`) complete. (Live PostgreSQL verification this
  session was blocked by the portable PG being killed when the headless shell
  exits; used SQLite in-memory test suite + offline Alembic `--sql` instead.)
- Frontend: `npm run build` (tsc + vite) OK; `npm run lint` clean (0 warnings).
  Real Login/Register + job management/browse/apply pages + ResumeManager,
  AuthContext, axios Bearer + 401-refresh interceptor, protected/role route
  guards all in place.
- Docker: Docker Desktop installed; `docker compose config` validates the full
  stack. Live `docker compose up` NOT yet run (Docker daemon needs admin
  elevation / WSL2-Hyper-V unavailable in this headless env).
- Database: LIVE connection VERIFIED in Stage 2 against portable PostgreSQL 17.

## Pending Work
- Install Docker Desktop + run `docker compose up --build`; confirm full stack
  boots with `database: ok`.
- Sprint 5: Resume Parsing (extract text from PDF/DOCX into profile fields).

## Next Objective
Begin **Sprint 5 — Resume Parsing** (text extraction from uploaded resumes),
or continue frontend dashboards. (No AI/interview work until those later sprints.)

## Known Issues
1. Live `docker compose up` cannot run here: the Docker daemon needs WSL2/
   Hyper-V, which require admin elevation (UAC) not available in this headless
   shell. The compose config itself is validated and ready; it will run once
   the daemon is available.
2. Requirements use `>=` lower bounds (not exact pins) so local Python 3.14
   resolves to compatible releases; Docker/CI use Python 3.12. Consider
   tightening pins once a lockfile is introduced.
3. `backend/.env` was created from `.env.example` (gitignored) so compose has
   its env file; replace the placeholder SECRET_KEY before any real deploy.
4. Temp PostgreSQL (portable, port 15432) is killed when the headless shell
   exits (children receive 0xC0000142). Restart it within the same shell as any
   dependent process for live verification.

## Known Issues
1. Live `docker compose up` cannot run here: the Docker daemon needs WSL2/
   Hyper-V, which require admin elevation (UAC) not available in this headless
   shell. The compose config itself is validated and ready; it will run once
   the daemon is available.
2. Requirements use `>=` lower bounds (not exact pins) so local Python 3.14
   resolves to compatible releases; Docker/CI use Python 3.12. Consider
   tightening pins once a lockfile is introduced.
3. `backend/.env` was created from `.env.example` (gitignored) so compose has
   its env file; replace the placeholder SECRET_KEY before any real deploy.
