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
    citations: list[RetrievedSource] = field(default_factory=list)


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

        return AgentAnswer(
            question=question,
            intent=final.get("intent", "knowledge_query"),
            answer=final.get("answer", ""),
            verified=final.get("verified", False),
            verification_notes=final.get("verification_notes", ""),
            citations=final.get("cited_sources", []),
        )
