from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import engine

router = APIRouter(tags=["health"])


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
