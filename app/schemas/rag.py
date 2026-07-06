"""Schemas for RAG ingestion and retrieval endpoints."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.chunk import ChunkSearchResult


class IngestResponse(BaseModel):
    """Result of ingesting a document into the vector store."""

    document_id: int
    chunks_created: int


class SearchRequest(BaseModel):
    """Payload for a similarity search."""

    query: str = Field(..., min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=50)
    document_id: int | None = None


class SearchResponse(BaseModel):
    """Top-K similarity search results for a query."""

    query: str
    results: list[ChunkSearchResult]
