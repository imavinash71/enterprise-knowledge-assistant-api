"""LangGraph node implementations for the knowledge-assistant workflow.

Each node is a plain method with the signature ``(state) -> partial_state``.
Nodes are grouped on :class:`KnowledgeAssistantNodes` so they can share
injected dependencies (retrieval + LLM) instead of relying on globals, keeping
the graph testable and consistent with the project's DI/service patterns.
"""
from __future__ import annotations

import re

from app.core.logging import get_logger
from app.rag.llm.base import LLMProvider
from app.services.retrieval_service import RetrievalService

from app.agents.state import AgentState, RetrievedSource

logger = get_logger(__name__)

# Matches citation markers such as "[1]" or "[12]" inside the generated answer.
_CITATION_RE = re.compile(r"\[(\d+)\]")

# Known intent labels. The LLM is asked to return one of these; anything else
# falls back to ``knowledge_query`` so the user still gets a document-grounded
# answer rather than being dropped into small talk.
_KNOWN_INTENTS = {"greeting", "knowledge_query", "chitchat"}


class KnowledgeAssistantNodes:
    """Container for the four workflow nodes and their routing helper."""

    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_provider: LLMProvider,
    ) -> None:
        self._retrieval = retrieval_service
        self._llm = llm_provider

    # ------------------------------------------------------------------ #
    # Node 1: Intent Analyzer
    # ------------------------------------------------------------------ #
    def intent_analyzer(self, state: AgentState) -> AgentState:
        """Classify the user's message so the graph can route appropriately."""
        question = state["question"]
        system = (
            "[TASK:intent] You are an intent classifier for a document Q&A "
            "assistant. Classify the user's message as exactly one of: "
            "'greeting', 'knowledge_query', or 'chitchat'. Respond with only "
            "the label."
        )
        raw = self._llm.generate(question, system=system).strip().lower()
        intent = raw if raw in _KNOWN_INTENTS else "knowledge_query"
        logger.info("Intent classified as '%s'", intent)
        return {"intent": intent}

    # ------------------------------------------------------------------ #
    # Node 2: Retriever
    # ------------------------------------------------------------------ #
    def retriever(self, state: AgentState) -> AgentState:
        """Fetch the most relevant chunks and number them for citation."""
        scored = self._retrieval.search(
            state["question"],
            owner_id=state.get("owner_id"),
            document_id=state.get("document_id"),
            top_k=state.get("top_k"),
        )
        sources: list[RetrievedSource] = [
            {
                "index": i,
                "chunk_id": item.chunk.id,
                "document_id": item.chunk.document_id,
                "content": item.chunk.content,
                "score": item.score,
            }
            for i, item in enumerate(scored, start=1)
        ]
        logger.info("Retriever attached %d sources to state", len(sources))
        return {"sources": sources}

    # ------------------------------------------------------------------ #
    # Node 3: Answer Generator
    # ------------------------------------------------------------------ #
    def answer_generator(self, state: AgentState) -> AgentState:
        """Generate an answer, grounding it in numbered sources when present."""
        intent = state.get("intent", "knowledge_query")
        sources = state.get("sources", [])

        # No documents to ground against: handle greetings/chitchat via a short
        # conversational reply, and be explicit when a knowledge query has no
        # supporting context rather than inventing an answer.
        if not sources:
            if intent == "knowledge_query":
                return {
                    "answer": (
                        "I could not find relevant information in your documents "
                        "to answer that question."
                    )
                }
            reply = self._llm.generate(
                state["question"],
                system=(
                    "[TASK:smalltalk] You are a friendly document assistant. "
                    "Reply briefly and invite the user to ask about their "
                    "documents."
                ),
            )
            return {"answer": reply}

        context = "\n".join(
            f"[{s['index']}] {s['content']}" for s in sources
        )
        prompt = (
            f"Question: {state['question']}\n\n"
            f"Sources:\n{context}\n\n"
            "Answer the question using ONLY the sources above. Cite each fact "
            "with its bracketed number, e.g. [1]. If the sources do not contain "
            "the answer, say so."
        )
        system = (
            "[TASK:answer] You are a precise knowledge assistant. Base your "
            "answer strictly on the provided sources and cite them inline."
        )
        answer = self._llm.generate(prompt, system=system)
        return {"answer": answer}

    # ------------------------------------------------------------------ #
    # Node 4: Citation Verifier
    # ------------------------------------------------------------------ #
    def citation_verifier(self, state: AgentState) -> AgentState:
        """Validate that every citation maps to a real retrieved source.

        Hallucinated markers (indices not in the source set) are stripped from
        the answer so the client never sees references it cannot resolve.
        """
        answer = state.get("answer", "")
        sources = state.get("sources", [])
        valid_indices = {s["index"] for s in sources}

        cited = [int(m) for m in _CITATION_RE.findall(answer)]
        cited_valid = sorted({i for i in cited if i in valid_indices})
        hallucinated = sorted({i for i in cited if i not in valid_indices})

        cleaned_answer = answer
        if hallucinated:
            # Remove markers that don't correspond to a retrieved source.
            def _strip(match: re.Match[str]) -> str:
                return "" if int(match.group(1)) in hallucinated else match.group(0)

            cleaned_answer = _CITATION_RE.sub(_strip, answer)
            # Collapse any double spaces left behind by removed markers.
            cleaned_answer = re.sub(r"\s{2,}", " ", cleaned_answer).strip()

        cited_sources = [s for s in sources if s["index"] in cited_valid]

        # An answer is "verified" when it makes at least one valid citation and
        # references nothing that wasn't retrieved. Answers with no sources
        # (greetings/chitchat) are considered verified by definition.
        if not sources:
            verified = True
            notes = "No retrieval performed; no citations required."
        elif not cited_valid:
            verified = False
            notes = "Answer did not cite any of the retrieved sources."
        elif hallucinated:
            verified = False
            notes = (
                f"Removed hallucinated citation markers: {hallucinated}. "
                f"Verified citations: {cited_valid}."
            )
        else:
            verified = True
            notes = f"All citations verified: {cited_valid}."

        logger.info("Citation verification: verified=%s notes=%s", verified, notes)
        return {
            "answer": cleaned_answer,
            "cited_indices": cited_valid,
            "cited_sources": cited_sources,
            "verified": verified,
            "verification_notes": notes,
        }

    # ------------------------------------------------------------------ #
    # Conditional routing
    # ------------------------------------------------------------------ #
    def route_after_intent(self, state: AgentState) -> str:
        """Send knowledge queries through retrieval; skip it for social turns."""
        return "retriever" if state.get("intent") == "knowledge_query" else "answer_generator"
