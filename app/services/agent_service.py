"""Agent service: orchestrates the LangGraph knowledge-assistant workflow.

Wraps graph construction and invocation behind a simple, typed method so the API
layer stays thin and unaware of LangGraph internals. Returns a plain result
object that maps cleanly onto the response schema.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.core.logging import get_logger
from app.rag.llm.base import LLMProvider
from app.services.retrieval_service import RetrievalService

from app.agents.graph import build_knowledge_graph
from app.agents.state import AgentState, RetrievedSource

logger = get_logger(__name__)


@dataclass
class AgentAnswer:
    """Structured result of an agent run."""

    question: str
    intent: str
    answer: str
    verified: bool
    verification_notes: str
    confidence: float
    # All chunks returned by retrieval (what informed the answer).
    sources: list[RetrievedSource] = field(default_factory=list)
    # The verified subset actually cited inline in the answer.
    citations: list[RetrievedSource] = field(default_factory=list)


def _confidence_score(
    intent: str, verified: bool, citations: list[RetrievedSource]
) -> float:
    """Derive a 0-1 confidence score for an answer.

    Social turns (greeting/chitchat) are deterministic canned replies, so they
    score 1.0. Knowledge answers score the mean similarity of their cited
    sources, halved when citation verification failed and 0.0 when nothing was
    cited (i.e. the answer is ungrounded).
    """
    if intent != "knowledge_query":
        return 1.0
    if not citations:
        return 0.0
    mean_score = sum(c["score"] for c in citations) / len(citations)
    if not verified:
        mean_score *= 0.5
    return round(max(0.0, min(1.0, mean_score)), 4)


class AgentService:
    """Runs the knowledge-assistant graph for a single question."""

    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_provider: LLMProvider,
    ) -> None:
        # Compile the graph once per service instance (per request via DI).
        self._graph = build_knowledge_graph(retrieval_service, llm_provider)

    def answer(
        self,
        question: str,
        *,
        owner_id: int | None = None,
        document_id: int | None = None,
        top_k: int | None = None,
    ) -> AgentAnswer:
        """Answer ``question`` using the agent workflow.

        Args:
            question: The user's natural-language message.
            owner_id: Restrict retrieval to this user's documents.
            document_id: Optionally restrict retrieval to one document.
            top_k: Number of chunks to retrieve.
        """
        initial: AgentState = {
            "question": question,
            "owner_id": owner_id,
            "document_id": document_id,
            "top_k": top_k,
        }
        logger.info("Running agent workflow for owner_id=%s", owner_id)
        final: AgentState = self._graph.invoke(initial)

        intent = final.get("intent", "knowledge_query")
        verified = final.get("verified", False)
        citations = final.get("cited_sources", [])
        return AgentAnswer(
            question=question,
            intent=intent,
            answer=final.get("answer", ""),
            verified=verified,
            verification_notes=final.get("verification_notes", ""),
            confidence=_confidence_score(intent, verified, citations),
            sources=final.get("sources", []),
            citations=citations,
        )
