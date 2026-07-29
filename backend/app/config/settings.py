from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    PROJECT_NAME: str = "HireMind AI"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = Field(default="change-me-in-production", repr=False)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: Any) -> Any:
        """Accept a comma-separated string or JSON list for CORS origins."""
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                return value
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return value

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "hiremind"
    POSTGRES_PASSWORD: str = Field(default="hiremind", repr=False)
    POSTGRES_DB: str = "hiremind_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" or "text"

    # Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 25

    # AI (Sprint 6 — question generation via NVIDIA's OpenAI-compatible API)
    NVIDIA_API_KEY: str = ""
    NVIDIA_MODEL: str = "nvidia/llama-3.3-nemotron-super-49b-v1"
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"

    # Optional explicit DB URL override (e.g. sqlite+aiosqlite:///./dev.db for
    # local dev without Postgres). When set, it takes precedence over the
    # POSTGRES_* settings for both sync and async connections.
    DATABASE_URL: str = ""

    @property
    def database_url(self) -> str:
        """Synchronous database URL for Alembic / scripts."""
        if self.DATABASE_URL:
            sync = self.DATABASE_URL.replace("+aiosqlite", "")
            return sync
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_url_async(self) -> str:
        """Asynchronous database URL for the running application."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def model_dump_public(self) -> dict[str, Any]:
        """Return a safe, non-secret view of the settings."""
        data = self.model_dump()
        data.pop("SECRET_KEY", None)
        data.pop("POSTGRES_PASSWORD", None)
        return data


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()
