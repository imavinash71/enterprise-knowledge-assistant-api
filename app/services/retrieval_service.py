"""Retrieval service: embed a query and fetch the most similar chunks."""
from __future__ import annotations

from app.core.config import settings
from app.core.logging import get_logger
from app.rag.embeddings.base import EmbeddingProvider
from app.repositories.chunk_repository import ChunkRepository, ScoredChunk

logger = get_logger(__name__)


class RetrievalService:
    """Performs vector similarity search over stored document chunks."""

    def __init__(
        self,
        chunk_repository: ChunkRepository,
        embedding_provider: EmbeddingProvider,
    ) -> None:
        self._chunks = chunk_repository
        self._embeddings = embedding_provider

    def search(
        self,
        query: str,
        *,
        owner_id: int | None = None,
        document_id: int | None = None,
        top_k: int | None = None,
    ) -> list[ScoredChunk]:
        """Return the top-K chunks most relevant to ``query``.

        Args:
            query: The natural-language search query.
            owner_id: Restrict results to documents owned by this user.
            document_id: Restrict results to a single document.
            top_k: Number of results to return (defaults to ``RAG_TOP_K``).
        """
        k = top_k or settings.RAG_TOP_K
        query_vector = self._embeddings.embed_query(query)
        results = self._chunks.similarity_search(
            query_vector,
            top_k=k,
            owner_id=owner_id,
            document_id=document_id,
        )
        logger.info("Similarity search returned %d chunks for query", len(results))
        return results
