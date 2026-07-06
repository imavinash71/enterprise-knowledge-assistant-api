"""Application configuration.

All settings are loaded from environment variables and/or a local ``.env``
file using :mod:`pydantic-settings`.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ------------------------------------------------------------------ #
    # Application
    # ------------------------------------------------------------------ #
    PROJECT_NAME: str = "Enterprise Knowledge Assistant API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ------------------------------------------------------------------ #
    # Server
    # ------------------------------------------------------------------ #
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ------------------------------------------------------------------ #
    # Logging
    # ------------------------------------------------------------------ #
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    # ------------------------------------------------------------------ #
    # CORS
    # ------------------------------------------------------------------ #
    # Stored as a raw comma-separated string to avoid pydantic-settings
    # attempting to JSON-decode a list-typed env var. Use ``cors_origins`` to
    # obtain the parsed list.
    BACKEND_CORS_ORIGINS: str = ""

    @property
    def cors_origins(self) -> list[str]:
        """Return CORS origins parsed from the comma-separated setting."""
        raw = self.BACKEND_CORS_ORIGINS.strip()
        if not raw:
            return []
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    # ------------------------------------------------------------------ #
    # Database
    # ------------------------------------------------------------------ #
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "enterprise_knowledge"

    # Optional full override.
    DATABASE_URL: str | None = None

    # ------------------------------------------------------------------ #
    # Vector store / embeddings
    # ------------------------------------------------------------------ #
    # Dimension of the embedding vectors stored in the ``chunks`` table.
    # Defaults to 1536 to match OpenAI ``text-embedding-3-small``.
    EMBEDDING_DIM: int = 1536

    @property
    def sqlalchemy_database_uri(self) -> str:
        """Return the SQLAlchemy connection string."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return str(
            PostgresDsn.build(
                scheme="postgresql+psycopg2",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )


@lru_cache
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""
    return Settings()


settings = get_settings()
