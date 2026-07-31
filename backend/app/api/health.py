from __future__ import annotations

import asyncio
import socket
from typing import Any
from urllib.parse import urlsplit

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config.settings import settings
from app.core.database import engine

router = APIRouter(tags=["health"])


@router.get("/debug/db", summary="DB diagnostics")
async def db_debug() -> dict[str, Any]:
    """Temporary diagnostics: what URL we use, TCP reachability, real asyncpg error."""
    url = settings.database_url_async
    parts = urlsplit(url)
    host = parts.hostname or ""
    port = parts.port or 5432
    out: dict[str, Any] = {
        "host": host,
        "port": port,
        "uses_pooler": "pooler" in host,
        "user": parts.username,
        "db": parts.path.lstrip("/"),
    }
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
        out["dns_ips"] = sorted({i[4][0] for i in infos})
    except Exception as e:
        out["dns_error"] = f"{type(e).__name__}: {e}"
    try:
        s = socket.create_connection((host, port), timeout=5)
        out["tcp_ok"] = True
        s.close()
    except Exception as e:
        out["tcp_ok"] = False
        out["tcp_error"] = f"{type(e).__name__}: {e}"
    try:
        e = create_async_engine(url)
        async with e.connect() as c:
            await asyncio.wait_for(c.execute(text("SELECT 1")), timeout=8)
        out["asyncpg_ok"] = True
        await e.dispose()
    except Exception as e:
        out["asyncpg_ok"] = False
        out["asyncpg_error"] = f"{type(e).__name__}: {str(e)[:500]}"
    return out


@router.get("/health", summary="Health check")
async def health_check() -> dict[str, Any]:
    """Return service health status. Verifies database connectivity with a timeout."""
    db_status = "ok"
    try:
        async with engine.connect() as conn:
            await asyncio.wait_for(conn.execute(text("SELECT 1")), timeout=3.0)
    except Exception:
        db_status = "unavailable"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "service": "hiremind-ai-backend",
        "database": db_status,
    }
