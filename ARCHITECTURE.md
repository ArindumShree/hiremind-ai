# ARCHITECTURE.md

Architecture documentation for HireMind AI. Updated whenever the architecture
changes.

===============================================================================

## 1. Architectural Style

**Chosen: Modular Monolith**

The system is a single deployable unit (one backend service, one frontend
bundle) but internally organized into well-separated feature modules with
clear boundaries.

**Why this choice?**
- Simplest option that still supports clean separation of concerns.
- No distributed-systems complexity (network failures, service discovery,
  message queues) while the team and feature set are small.
- Easy to reason about, test, and deploy for a portfolio / placement project.
- Can later be split into microservices if scale demands it.

**Alternative considered: Microservices**
- Rejected for now: adds significant operational overhead (API gateway,
  inter-service auth, separate databases, deployment pipelines) that is not
  justified at this stage. The modular boundaries keep the future migration
  path open without paying the cost today.

**Alternative considered: Pure Monolith (no modules)**
- Rejected: leads to god-classes and tangled imports, violating the clean
  architecture and SOLID requirements stated in the brief.

===============================================================================

## 2. Technology Decisions

| Layer        | Technology            | Reason                                            |
|--------------|-----------------------|---------------------------------------------------|
| Frontend     | React + TypeScript    | Component model + type safety for maintainability |
| Build (FE)   | Vite                  | Fast dev server, simple config                    |
| Styling      | TailwindCSS           | Utility-first, consistent design without bloat    |
| Backend      | FastAPI               | Async, auto OpenAPI docs, Python type hints       |
| ORM          | SQLAlchemy            | Mature, explicit models, Alembic support          |
| Migrations   | Alembic               | Standard SQLAlchemy migration tool                |
| Database     | PostgreSQL            | Robust relational DB, JSON support, free tier ok  |
| Auth         | JWT                   | Stateless auth, standard for SPAs                 |
| AI           | Gemini API            | Question generation + qualitative feedback        |
| Speech       | Whisper               | Open-source transcription                         |
| Video        | MediaPipe + OpenCV    | Lightweight on-device signal extraction           |
| Deploy       | Docker + Compose      | Reproducible local + prod environments            |

===============================================================================

## 3. Application Layers (Backend)

```
api/            -> HTTP layer: routers, request/response schemas, deps
services/       -> Business logic per domain (auth, jobs, interview...)
repositories/   -> Data access abstraction over SQLAlchemy models
models/         -> SQLAlchemy ORM entities
schemas/        -> Pydantic DTOs
core/           -> Config, security, logging, error handling, db session
```

Dependency direction: `api -> services -> repositories -> models`.
Inner layers never import outer layers (Clean Architecture).

===============================================================================

## 4. Folder Structure (Planned)

```
hiremind-ai/
├── frontend/        # React + Vite + TS + Tailwind
├── backend/         # FastAPI + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── core/
│   ├── alembic/
│   └── tests/
├── docker-compose.yml
├── README.md
└── docs/ (this set of markdown files)
```

===============================================================================

## 5. Database Structure (High Level)

- **User**: id (UUID), full_name, email (unique), password_hash, role
  (candidate|recruiter), is_active, is_verified, created_at, updated_at
- **Profile**: id, user_id (FK, 1:1), phone, college, company, linkedin_url,
  github_url, bio, profile_picture, timestamps
- **RefreshToken**: id, jti (unique, hashed lookup), user_id (FK), expires_at,
  revoked
- **Candidate**: user_id, name, resume_path, parsed_profile (JSON)  *(Sprint 4+)*
- **Recruiter**: user_id, company, name  *(deferred; recruiter is a User role)*
- **Job**: id, posted_by (FK users), title, company_name, location,
  employment_type, experience_required, salary_range, description,
  requirements, responsibilities, skills_required, status
  (draft/published/closed/archived), is_deleted, deleted_at, timestamps
  *(Sprint 3 — implemented, soft-delete)*
- **Application**: id, candidate_id (FK users), job_id (FK jobs), status
  (applied/shortlisted/interview_scheduled/interview_completed/rejected/hired),
  cover_letter, applied_at, updated_at; UNIQUE(candidate_id, job_id)
  *(Sprint 3 — implemented)*
- **Resume**: id, candidate_id (FK users, UNIQUE, cascade), filename,
  stored_path, content_type, size_bytes, created_at; one resume per candidate,
  files stored under `uploads/candidates/<id>/` *(Sprint 4 — implemented)*
- **Interview**: id, application_id, status, started_at, completed_at  *(Stage 7)*
- **Evaluation**: id, interview_id, scores (JSON), feedback, created_at  *(Stage 10)*

(User, Profile, RefreshToken implemented in Sprint 2. Job + Application
implemented in Sprint 3. Resume implemented in Sprint 4. Rest finalized in
later sprints.)

===============================================================================

## 6. API Design

- RESTful JSON APIs under versioned prefix `/api/v1`.
- Standard responses: `{ "data": ..., "message": ... }`.
- Centralized error envelope with error codes.
- OpenAPI docs auto-generated by FastAPI at `/docs`.

===============================================================================

## 7. Authentication Flow

1. Candidate/Recruiter registers (email + password).
2. Password hashed with argon2 (passlib); user stored with role (candidate |
   recruiter) and a 1:1 profile.
3. Login returns JWT access (HS256, short-lived) + refresh tokens.
4. Access token sent as `Authorization: Bearer <token>` on protected routes;
   backend validates via FastAPI dependency (`get_current_user`).
5. Refresh endpoint rotates the refresh token and revokes the old one (jti
   stored hashed; raw token never persisted). Logout revokes the refresh token.
6. Frontend stores tokens in localStorage; axios interceptor attaches the
   Bearer token and transparently refreshes on 401, falling back to /login.
7. Role-based access via `require_role` dependency (backend) and
   `ProtectedRoute roles=[...]` guard (frontend).

(Implemented in Sprint 2.)

===============================================================================

## 8. AI Pipeline

1. Resume parsed -> structured candidate profile (Sprint 5).
2. Job + profile -> NVIDIA API generates tailored questions (Sprint 6).
3. Candidate answers via text/audio/video (Sprint 7).
4. Audio -> Whisper transcription; Video -> MediaPipe/OpenCV signals
   (Sprints 8-9).
5. Evaluation engine combines signals + Gemini feedback (Sprint 10).

===============================================================================
