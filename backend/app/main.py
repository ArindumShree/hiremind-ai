from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analysis import router as analysis_router
from app.api.application import candidate_router as application_candidate_router
from app.api.application import router as application_router
from app.api.auth import router as auth_router
from app.api.candidate import router as candidates_router
from app.api.health import router as health_router
from app.api.interview import router as interview_router
from app.api.job import router as job_router
from app.api.profile import router as profile_router
from app.api.question import router as question_router
from app.api.resume import router as resume_router
from app.config.settings import settings
from app.core.logging import get_logger
from app.middleware.exceptions import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Application factory that wires up middleware, routers and handlers."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="HireMind AI — AI-powered Hiring Intelligence Platform.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(app)

    app.include_router(health_router, prefix=settings.API_V1_PREFIX)
    app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
    app.include_router(profile_router, prefix=settings.API_V1_PREFIX)
    app.include_router(job_router, prefix=settings.API_V1_PREFIX)
    app.include_router(application_router, prefix=settings.API_V1_PREFIX)
    app.include_router(application_candidate_router, prefix=settings.API_V1_PREFIX)
    app.include_router(candidates_router, prefix=settings.API_V1_PREFIX)
    app.include_router(resume_router, prefix=settings.API_V1_PREFIX)
    app.include_router(interview_router, prefix=settings.API_V1_PREFIX)
    app.include_router(question_router, prefix=settings.API_V1_PREFIX)
    app.include_router(analysis_router, prefix=settings.API_V1_PREFIX)

    logger.info("Application startup complete")
    return app


app = create_app()
