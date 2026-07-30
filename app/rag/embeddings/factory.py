"""Factory for selecting an embedding provider from configuration."""
from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.core.exceptions import AppException
from app.rag.embeddings.base import EmbeddingProvider
from app.rag.embeddings.fake_provider import FakeEmbeddingProvider
from app.rag.embeddings.gemini_provider import GeminiEmbeddingProvider
from app.rag.embeddings.ollama_provider import OllamaEmbeddingProvider
from app.rag.embeddings.openai_provider import OpenAIEmbeddingProvider

_PROVIDERS = {
    "fake": FakeEmbeddingProvider,
    "openai": OpenAIEmbeddingProvider,
    "gemini": GeminiEmbeddingProvider,
    "ollama": OllamaEmbeddingProvider,
}


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    """Return the configured embedding provider (cached as a singleton).

    Raises:
        AppException: If ``EMBEDDING_PROVIDER`` is not a known provider.
    """
    key = settings.EMBEDDING_PROVIDER.lower()
    provider_cls = _PROVIDERS.get(key)
    if provider_cls is None:
        supported = ", ".join(sorted(_PROVIDERS))
        raise AppException(
            f"Unknown embedding provider '{key}'. Supported: {supported}.",
            error_code="config_error",
        )
    return provider_cls()
