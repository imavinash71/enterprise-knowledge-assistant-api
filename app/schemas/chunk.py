"""Pydantic schemas for the ``Chunk`` entity."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChunkBase(BaseModel):
    """Shared chunk fields."""

    content: str


class ChunkCreate(ChunkBase):
    """Payload for creating a chunk.

    ``embedding`` is optional at creation time because it may be generated
    asynchronously by the ingestion pipeline.
    """

    document_id: int
    embedding: list[float] | None = None


class ChunkRead(ChunkBase):
    """Chunk representation returned to clients.

    The raw ``embedding`` vector is intentionally omitted from the default read
    schema to keep payloads small; expose it explicitly where needed.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int


class ChunkSearchResult(ChunkRead):
    """A chunk returned from a similarity search, with its distance score."""

    score: float = Field(..., description="Vector distance / similarity score.")
