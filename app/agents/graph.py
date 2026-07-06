"""Assembles the knowledge-assistant workflow as a compiled LangGraph.

Flow:
    question
      -> intent_analyzer
           -> (knowledge_query) -> retriever -> answer_generator
           -> (greeting/chitchat)             -> answer_generator
      -> answer_generator -> citation_verifier -> END

The graph is built from injected services so it can be constructed per request
with request-scoped dependencies (DB session, embedding/LLM providers).
"""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.core.logging import get_logger
from app.rag.llm.base import LLMProvider
from app.services.retrieval_service import RetrievalService

from app.agents.nodes import KnowledgeAssistantNodes
from app.agents.state import AgentState

logger = get_logger(__name__)


def build_knowledge_graph(
    retrieval_service: RetrievalService,
    llm_provider: LLMProvider,
):
    """Build and compile the agent workflow graph.

    Args:
        retrieval_service: Provides vector similarity search over chunks.
        llm_provider: Generates intent labels and answers.

    Returns:
        A compiled LangGraph runnable accepting/returning :class:`AgentState`.
    """
    nodes = KnowledgeAssistantNodes(retrieval_service, llm_provider)

    graph = StateGraph(AgentState)
    graph.add_node("intent_analyzer", nodes.intent_analyzer)
    graph.add_node("retriever", nodes.retriever)
    graph.add_node("answer_generator", nodes.answer_generator)
    graph.add_node("citation_verifier", nodes.citation_verifier)

    graph.set_entry_point("intent_analyzer")

    # Route based on the classified intent: only knowledge queries need the
    # retrieval step; social turns go straight to generation.
    graph.add_conditional_edges(
        "intent_analyzer",
        nodes.route_after_intent,
        {
            "retriever": "retriever",
            "answer_generator": "answer_generator",
        },
    )
    graph.add_edge("retriever", "answer_generator")
    graph.add_edge("answer_generator", "citation_verifier")
    graph.add_edge("citation_verifier", END)

    compiled = graph.compile()
    logger.info("Knowledge-assistant graph compiled")
    return compiled
