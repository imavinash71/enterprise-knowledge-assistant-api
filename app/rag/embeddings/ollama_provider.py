"""Ollama embedding provider.

Generates embeddings from a self-hosted or remote `Ollama <https://ollama.com>`_
server via its HTTP ``/api/embeddings`` endpoint. No API key is required — only
a reachable base URL (``OLLAMA_BASE_URL``). Pair with an embedding model such as
``nomic-embed-text`` (768-dim); set ``EMBEDDING_DIM`` to match.
"""
from __future__ import annotations

from app.core.config import settings
from app.core.exceptions import AppException
from app.rag.embeddings.base import EmbeddingProvider


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Embeddings backed by an Ollama server's ``/api/embeddings`` endpoint.

    The ``requests`` import is deferred to call time so importing this module
    never requires the dependency unless the provider is actually used.
    """

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        dimension: int | None = None,
        timeout: float | None = None,
    ) -> None:
        self._model = model or settings.OLLAMA_EMBEDDING_MODEL
        self._base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self._dimension = dimension or settings.EMBEDDING_DIM
        self._timeout = settings.OLLAMA_TIMEOUT if timeout is None else timeout

    @property
    def dimension(self) -> int:
        return self._dimension

    def _embed_one(self, text: str) -> list[float]:
        try:
            import requests
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise AppException(
                "The 'requests' package is required for the Ollama embedding "
                "provider."
            ) from exc

        url = f"{self._base_url}/api/embeddings"
        try:
            response = requests.post(
                url,
                json={"model": self._model, "prompt": text},
                timeout=self._timeout,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise AppException(
                f"Ollama embedding request to {url} failed: {exc}",
                error_code="embedding_provider_error",
            ) from exc

        embedding = response.json().get("embedding")
        if not embedding:
            raise AppException(
                "Ollama embedding response did not contain an 'embedding'.",
                error_code="embedding_provider_error",
            )
        return [float(value) for value in embedding]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Ollama's embeddings endpoint accepts a single prompt per call, so we
        # embed each text sequentially. (nomic-embed-text is fast enough for
        # typical document sizes.)
        return [self._embed_one(text) for text in texts]
