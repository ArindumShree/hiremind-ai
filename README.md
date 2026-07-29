# HireMind AI

> AI-powered Hiring Intelligence Platform that automates first-round technical interviews.

HireMind AI streamlines early-stage technical screening by combining AI-generated interview questions, candidate answer evaluation, and multimodal analysis (speech/video) into a single scoreable evaluation.

---

## Quick Start (Local — no Docker)

### Prerequisites

- Python 3.12+
- Node.js 20+
- Git

### 1. Clone

```bash
git clone https://github.com/ArindumShree/hiremind-ai.git
cd hiremind-ai
```

### 2. Backend setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
```

Open `backend/.env` and set your **NVIDIA API key** (required for AI features):
```
NVIDIA_API_KEY=nvapi-your-key-here
```

Get a free key at [build.nvidia.com](https://build.nvidia.com/).

### 3. Frontend setup

```bash
cd frontend
npm install
```

### 4. Run

From the `hiremind-ai` root:

```powershell
# Windows
.\run-local.ps1
```

Or manually:

```bash
# Terminal 1 — backend
cd backend
.venv\Scripts\activate
$env:DATABASE_URL="sqlite+aiosqlite:///./dev.db"
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev -- --host
```

- **Frontend**: http://localhost:5173
- **API docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/v1/health

### 5. Seed demo data (optional)

With the backend running, open another terminal and run:

```powershell
powershell -ExecutionPolicy Bypass -File C:\path\to\seed.ps1
```

This creates 2 recruiters, 4 candidates, 4 job postings, applications, and a fully evaluated interview. Login with any account:

| Email | Role | Password |
|---|---|---|
| `r1@hiremind.demo` | Recruiter (Acme Corp) | `Password123!` |
| `r2@hiremind.demo` | Recruiter (Globex Inc) | `Password123!` |
| `c1@hiremind.demo` | Candidate (Alice/MIT) | `Password123!` |
| `c2@hiremind.demo` | Candidate (Bob/Stanford) | `Password123!` |
| `c3@hiremind.demo` | Candidate (Carol/Berkeley) | `Password123!` |
| `c4@hiremind.demo` | Candidate (David/Georgia Tech) | `Password123!` |

### 6. Stop the servers

```powershell
Get-NetTCPConnection -LocalPort 8000,5173 -ErrorAction SilentlyContinue |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, TailwindCSS |
| Routing | React Router 6 |
| State/API | TanStack Query, Axios |
| Backend | FastAPI, Pydantic v2 |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Database | PostgreSQL 17 (prod) / SQLite (local dev) |
| Auth | JWT (access + refresh tokens) |
| AI | NVIDIA NIM (LLaMA 3.3 Nemotron) |
| Speech | Whisper (via OpenAI-compatible API) |
| Video | OpenCV (cv2) |
| Deploy | Docker, Docker Compose |

---

## Project Structure

```
hiremind-ai/
├── frontend/                 # React + Vite + TS + Tailwind
│   ├── src/
│   │   ├── pages/            # UI pages
│   │   ├── components/       # Reusable components
│   │   ├── layouts/          # Layout + nav
│   │   ├── services/         # API clients
│   │   ├── hooks/            # Custom hooks
│   │   └── App.tsx
│   ├── Dockerfile
│   └── nginx.conf
├── backend/                  # FastAPI + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── api/              # Route handlers
│   │   ├── core/             # Config, DB, logging, security
│   │   ├── config/           # Settings (pydantic-settings)
│   │   ├── models/           # SQLAlchemy entities
│   │   ├── schemas/          # Pydantic DTOs
│   │   ├── services/         # Business logic
│   │   ├── repositories/     # Data access layer
│   │   └── middleware/       # Exception + request logging
│   ├── alembic/              # Migration scripts
│   ├── tests/                # pytest suite (50+ tests)
│   ├── Dockerfile
│   └── requirements.txt
├── .github/workflows/ci.yml  # CI pipeline
├── docker-compose.yml
└── run-local.ps1              # One-command local launcher
```

---

## Running with Docker

```bash
docker compose up --build
```

You'll still need to set `NVIDIA_API_KEY` in `backend/.env` before building.

---

## Development

| Command | Location | Action |
|---|---|---|
| `ruff check .` | `backend/` | Lint Python |
| `pytest` | `backend/` | Run tests |
| `alembic upgrade head` | `backend/` | Apply migrations |
| `npm run lint` | `frontend/` | Lint frontend |
| `npm run build` | `frontend/` | Build frontend |

---

## Roles & Features

- **Recruiters**: Post jobs, shortlist candidates, start AI interviews, review answer scores + speech/video analysis, view candidates side-by-side.
- **Candidates**: Upload resume, browse/publish jobs, apply, take AI-generated interviews (text + optional audio/video answers).

---

## License

MIT
