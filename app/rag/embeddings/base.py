"""Embedding provider strategy interface."""
from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Strategy for generating embedding vectors from text.

    Two methods are exposed because some providers embed documents and queries
    differently (e.g. task-type hints). The default query implementation simply
    delegates to :meth:`embed_documents`.
    """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the dimensionality of the vectors produced."""
        raise NotImplementedError

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of documents/passages."""
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        """Embed a single search query."""
        return self.embed_documents([text])[0]
