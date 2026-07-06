"""Deterministic local embedding provider (no external API).

Produces normalized pseudo-random vectors seeded by a hash of the input text,
so the same text always yields the same vector. This makes the full RAG
pipeline runnable and testable without any API key or network access. It is not
semantically meaningful and must not be used in production retrieval quality.
"""
from __future__ import annotations

import hashlib

import numpy as np

from app.core.config import settings
from app.rag.embeddings.base import EmbeddingProvider


class FakeEmbeddingProvider(EmbeddingProvider):
    """Hash-seeded, L2-normalized embeddings for development and testing."""

    def __init__(self, dimension: int | None = None) -> None:
        self._dimension = dimension or settings.EMBEDDING_DIM

    @property
    def dimension(self) -> int:
        return self._dimension

    def _embed_one(self, text: str) -> list[float]:
        # Seed a RNG deterministically from the text so results are stable.
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(digest[:8], "big")
        rng = np.random.default_rng(seed)
        vector = rng.standard_normal(self._dimension)
        # L2-normalize so cosine distance behaves well.
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector.astype(float).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]
