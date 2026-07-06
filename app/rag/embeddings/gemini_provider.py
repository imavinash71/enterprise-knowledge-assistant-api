"""Google Gemini embedding provider."""
from __future__ import annotations

from app.core.config import settings
from app.core.exceptions import AppException
from app.rag.embeddings.base import EmbeddingProvider

# Gemini's ``text-embedding-004`` returns 768-dimensional vectors; set
# EMBEDDING_DIM=768 when using this provider.
_DEFAULT_GEMINI_MODEL = "models/text-embedding-004"


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Embeddings backed by Google's Generative AI (Gemini) API."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        dimension: int | None = None,
    ) -> None:
        self._model = model or _DEFAULT_GEMINI_MODEL
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._dimension = dimension or settings.EMBEDDING_DIM
        self._configured = False

    def _ensure_configured(self):
        if self._configured:
            return
        if not self._api_key:
            raise AppException(
                "GEMINI_API_KEY is not configured.", error_code="config_error"
            )
        try:
            import google.generativeai as genai
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise AppException(
                "The 'google-generativeai' package is required for the Gemini "
                "provider."
            ) from exc
        genai.configure(api_key=self._api_key)
        self._genai = genai
        self._configured = True

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        self._ensure_configured()
        result = self._genai.embed_content(
            model=self._model,
            content=texts,
            task_type="retrieval_document",
        )
        return result["embedding"]

    def embed_query(self, text: str) -> list[float]:
        self._ensure_configured()
        result = self._genai.embed_content(
            model=self._model,
            content=text,
            task_type="retrieval_query",
        )
        return result["embedding"]
