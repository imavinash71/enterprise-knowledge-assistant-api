"""Factory for selecting an LLM provider from configuration."""
from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.core.exceptions import AppException
from app.rag.llm.base import LLMProvider
from app.rag.llm.fake_provider import FakeLLMProvider
from app.rag.llm.gemini_provider import GeminiLLMProvider
from app.rag.llm.ollama_provider import OllamaLLMProvider
from app.rag.llm.openai_provider import OpenAILLMProvider

_PROVIDERS = {
    "fake": FakeLLMProvider,
    "openai": OpenAILLMProvider,
    "gemini": GeminiLLMProvider,
    "ollama": OllamaLLMProvider,
}


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Return the configured LLM provider (cached as a singleton).

    Raises:
        AppException: If ``LLM_PROVIDER`` is not a known provider.
    """
    key = settings.LLM_PROVIDER.lower()
    provider_cls = _PROVIDERS.get(key)
    if provider_cls is None:
        supported = ", ".join(sorted(_PROVIDERS))
        raise AppException(
            f"Unknown LLM provider '{key}'. Supported: {supported}.",
            error_code="config_error",
        )
    return provider_cls()
