"""OpenAI embedding provider."""
from __future__ import annotations

from functools import cached_property

from app.core.config import settings
from app.core.exceptions import AppException
from app.rag.embeddings.base import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Embeddings backed by the OpenAI Embeddings API.

    The ``openai`` package and client are created lazily so importing this
    module never requires the dependency or an API key unless the provider is
    actually used.
    """

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        dimension: int | None = None,
    ) -> None:
        self._model = model or settings.EMBEDDING_MODEL
        self._api_key = api_key or settings.OPENAI_API_KEY
        self._dimension = dimension or settings.EMBEDDING_DIM

    @cached_property
    def _client(self):
        if not self._api_key:
            raise AppException(
                "OPENAI_API_KEY is not configured.", error_code="config_error"
            )
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise AppException(
                "The 'openai' package is required for the OpenAI provider."
            ) from exc
        return OpenAI(api_key=self._api_key)

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self._client.embeddings.create(
            model=self._model,
            input=texts,
            # ``dimensions`` lets newer models return a specific vector size.
            dimensions=self._dimension,
        )
        return [item.embedding for item in response.data]
