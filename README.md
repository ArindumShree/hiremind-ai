# HireMind AI

> AI-powered Hiring Intelligence Platform that automates first-round technical interviews.

HireMind AI streamlines early-stage technical screening by combining resume
parsing, AI-generated questions, and multimodal interview analysis (speech and
video signals) into a single, scoreable evaluation. This repository is
structured as a production-style **Modular Monolith**.

---

## Architecture

- **Style:** Modular Monolith (single deployable backend + single frontend bundle).
- **Backend:** FastAPI (async) with SQLAlchemy 2.0, Alembic migrations, PostgreSQL.
- **Frontend:** React + TypeScript + Vite, TailwindCSS, React Router, TanStack Query.
- **AI / Media:** Gemini API (questions & feedback), Whisper (speech), MediaPipe + OpenCV (video).
- **Deployment:** Docker + Docker Compose.

Dependency direction (backend): `api -> services -> repositories -> models`.
Inner layers never import outer layers (Clean Architecture).

---

## Tech Stack

| Layer        | Technology                                  |
|--------------|---------------------------------------------|
| Frontend     | React, TypeScript, Vite, TailwindCSS        |
| Routing      | React Router                                |
| Data fetching| TanStack Query, Axios                       |
| Backend      | FastAPI, Pydantic                           |
| ORM          | SQLAlchemy 2.0 (async)                      |
| Migrations   | Alembic                                     |
| Database     | PostgreSQL 17                               |
| Auth         | JWT (planned, Stage 2)                      |
| AI           | Gemini API (planned)                        |
| Speech       | Whisper (planned)                           |
| Video        | MediaPipe + OpenCV (planned)                |
| Deploy       | Docker, Docker Compose                      |

---

## Folder Structure

```
hiremind-ai/
├── frontend/                 # React + Vite + TS + Tailwind
│   ├── src/
│   │   ├── pages/            # Placeholder pages (Home, Login, ...)
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── services/         # API client
│   │   ├── hooks/
│   │   └── App.tsx
│   ├── Dockerfile
│   └── nginx.conf
├── backend/                  # FastAPI + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── api/              # Routers (health)
│   │   ├── core/            # Config, db, logging, errors
│   │   ├── config/          # Settings (pydantic-settings)
│   │   ├── models/          # SQLAlchemy entities
│   │   ├── schemas/         # Pydantic DTOs
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── middleware/       # Exception + request logging
│   │   └── utils/
│   ├── alembic/             # Migration env
│   ├── tests/
│   ├── uploads/             # resume/ and videos/ (gitignored contents)
│   ├── Dockerfile
│   └── requirements.txt
├── docker/                   # Shared Docker config
├── docs/                     # Project documentation (markdown)
├── .github/workflows/ci.yml  # Base CI
├── docker-compose.yml
└── README.md
```

---

## Installation

### Prerequisites

- Git
- Docker Desktop (recommended) **or** local Python 3.12+ and Node.js 20+
- PostgreSQL 17 (only if running locally without Docker)

### 1. Clone

```bash
git clone <repo-url>
cd hiremind-ai
```

### 2. Configure environment

```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your secrets (do NOT commit real secrets)
```

---

## Running Locally (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

- App: http://localhost:5173

---

## Running with Docker

From the repository root:

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs
- PostgreSQL available on `localhost:5432`

To run in detached mode: `docker compose up -d --build`.

---

## Development Workflow

- **Backend**
  - Lint: `ruff check .`
  - Test: `pytest`
  - Migrations: `alembic revision --autogenerate -m "msg"` then `alembic upgrade head`
- **Frontend**
  - Dev server: `npm run dev`
  - Lint: `npm run lint`
  - Format: `npm run format`
  - Build: `npm run build`
- **Conventions**
  - PEP8, SOLID, Clean Architecture on the backend.
  - No hardcoded secrets — all configuration via `.env`.
  - Meaningful naming, reusable code, proper logging and error handling.

---

## Future Roadmap

| Stage | Scope |
|-------|-------|
| 1 (done) | Project foundation: scaffolding, config, logging, errors, health, Docker. |
| 2 | Authentication (JWT, roles). |
| 3 | Database models + migrations. |
| 4 | Resume upload. |
| 5 | Resume parsing. |
| 6 | AI question generation (Gemini). |
| 7 | Interview module. |
| 8 | Speech analysis (Whisper). |
| 9 | Video analysis (MediaPipe + OpenCV). |
| 10 | Evaluation engine. |
| 11 | Recruiter dashboard. |
| 12 | Production deployment. |

See `ROADMAP.md`, `ARCHITECTURE.md`, and `TASKS.md` for details.
