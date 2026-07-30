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
    # Authentication / JWT
    # ------------------------------------------------------------------ #
    # SECRET_KEY must be overridden in every non-development environment.
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ------------------------------------------------------------------ #
    # Vector store / embeddings
    # ------------------------------------------------------------------ #
    # Dimension of the embedding vectors stored in the ``chunks`` table.
    # Defaults to 1536 to match OpenAI ``text-embedding-3-small``.
    EMBEDDING_DIM: int = 1536

    # Embedding provider: "openai", "gemini", "ollama", or "fake". The "fake"
    # provider generates deterministic local vectors so the pipeline works
    # end-to-end without any external API key (useful for development and
    # testing). NOTE: "fake" is non-semantic — use a real provider for
    # meaningful retrieval quality.
    EMBEDDING_PROVIDER: str = "fake"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    # Ollama embeddings (self-hosted / remote). Used only when
    # EMBEDDING_PROVIDER="ollama". Reuses OLLAMA_BASE_URL / OLLAMA_TIMEOUT
    # defined in the LLM section. ``nomic-embed-text`` returns 768-dim vectors,
    # so set EMBEDDING_DIM=768 when using it.
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"

    # ------------------------------------------------------------------ #
    # LLM (answer generation / agents)
    # ------------------------------------------------------------------ #
    # LLM provider: "openai", "gemini", "ollama", or "fake". The "fake" provider
    # returns deterministic, citation-aware text so the LangGraph workflow runs
    # without any external API key.
    LLM_PROVIDER: str = "fake"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.0

    # Ollama (self-hosted / remote OpenAI-compatible LLM runtime). Used only
    # when LLM_PROVIDER="ollama". Points at the host running the Ollama server;
    # no API key is required.
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    # Per-request timeout (seconds) for the Ollama HTTP call.
    OLLAMA_TIMEOUT: float = 120.0


    # ------------------------------------------------------------------ #
    # RAG / chunking / retrieval
    # ------------------------------------------------------------------ #
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RAG_TOP_K: int = 5

    # ------------------------------------------------------------------ #
    # File uploads
    # ------------------------------------------------------------------ #
    # Directory (relative to the project root or absolute) where uploaded
    # files are stored.
    UPLOAD_DIR: str = "uploads"
    # Maximum accepted upload size, in megabytes.
    MAX_UPLOAD_SIZE_MB: int = 25

    @property
    def max_upload_size_bytes(self) -> int:
        """Return the maximum upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def allowed_upload_extensions(self) -> frozenset[str]:
        """Return the set of permitted (lower-cased) file extensions."""
        return frozenset({".pdf", ".docx", ".txt", ".pptx"})

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
