"""Shared state for the knowledge-assistant LangGraph workflow.

LangGraph passes a single mutable state dict between nodes. Each node reads the
keys it needs and returns a partial dict of updates, which LangGraph merges into
the running state. ``total=False`` lets nodes populate keys incrementally.
"""
from __future__ import annotations

from typing import TypedDict


class RetrievedSource(TypedDict):
    """A single retrieved chunk, numbered for citation in the answer."""

    index: int  # 1-based citation marker, e.g. [1]
    chunk_id: int
    document_id: int
    content: str
    score: float


class AgentState(TypedDict, total=False):
    """State threaded through the agent graph.

    Inputs (set before invocation):
        question: The user's message.
        owner_id: Restrict retrieval to this user's documents.
        document_id: Optionally restrict retrieval to one document.
        top_k: Number of chunks to retrieve.

    Produced by nodes:
        intent: Classified intent (greeting / knowledge_query / chitchat).
        sources: Numbered chunks returned by the retriever.
        answer: The generated (and citation-cleaned) answer.
        cited_indices: Source indices actually referenced by the answer.
        cited_sources: The subset of ``sources`` that were cited and verified.
        verified: Whether every citation in the answer maps to a real source.
        verification_notes: Human-readable notes from the verifier.
    """

    # Inputs
    question: str
    owner_id: int | None
    document_id: int | None
    top_k: int | None

    # Node outputs
    intent: str
    sources: list[RetrievedSource]
    answer: str
    cited_indices: list[int]
    cited_sources: list[RetrievedSource]
    verified: bool
    verification_notes: str
