# Launches HireMind AI locally (backend + frontend) for a demo.
# Backend: SQLite (backend/dev.db), port 8000. Frontend: Vite, port 5173 (exposed on LAN via --host).
# Run from the hiremind-ai root, e.g.:  powershell -ExecutionPolicy Bypass -File run-local.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"

# --- backend env (SQLite so no Postgres needed) ---
$env:DATABASE_URL = "sqlite+aiosqlite:///./dev.db"
$env:ENVIRONMENT = "development"
if (-not $env:SECRET_KEY) { $env:SECRET_KEY = "dev-secret-change-me-please" }

Write-Host "==> Running migrations (SQLite)..."
Push-Location $backend
try {
    & ".\.venv\Scripts\alembic.exe" upgrade head
} finally {
    Pop-Location
}

Write-Host "==> Starting backend on http://0.0.0.0:8000 ..."
Start-Process -FilePath (Join-Path $backend ".venv\Scripts\uvicorn.exe") `
    -ArgumentList "app.main:app","--host","0.0.0.0","--port","8000" `
    -WorkingDirectory $backend `
    -RedirectStandardOutput "$env:TEMP\hiremind-be.out" `
    -RedirectStandardError "$env:TEMP\hiremind-be.err" `
    -NoNewWindow

Write-Host "==> Starting frontend on http://0.0.0.0:5173 (LAN exposed) ..."
Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c","npm run dev -- --host" `
    -WorkingDirectory $frontend `
    -RedirectStandardOutput "$env:TEMP\hiremind-fe.out" `
    -RedirectStandardError "$env:TEMP\hiremind-fe.err" `
    -NoNewWindow

Write-Host ""
Write-Host "DONE. Open in a browser:"
Write-Host "  Frontend : http://localhost:5173   (or http://<this-machine-IP>:5173 for others on the network)"
Write-Host "  API docs : http://localhost:8000/docs"
Write-Host ""
Write-Host "Logs: $env:TEMP\hiremind-be.out / hiremind-fe.out"
Write-Host "Press Ctrl+C here does NOT stop them; to stop, close the uvicorn/vite processes."
