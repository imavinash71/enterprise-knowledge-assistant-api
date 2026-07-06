"""Schemas for the agent (LangGraph knowledge-assistant) endpoint."""
from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Payload for asking the knowledge assistant a question."""

    question: str = Field(..., min_length=1)
    document_id: int | None = Field(
        default=None, description="Restrict retrieval to a single document."
    )
    top_k: int | None = Field(default=None, ge=1, le=50)


class CitationOut(BaseModel):
    """A verified citation returned alongside the answer."""

    index: int
    chunk_id: int
    document_id: int
    content: str
    score: float


class AskResponse(BaseModel):
    """The agent's answer with its intent and verified citations."""

    question: str
    intent: str
    answer: str
    verified: bool
    verification_notes: str
    citations: list[CitationOut]
