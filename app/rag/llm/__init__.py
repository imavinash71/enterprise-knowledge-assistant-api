"""LLM providers for answer generation and agent reasoning.

Mirrors the embeddings package: a provider-agnostic interface with concrete
OpenAI/Gemini strategies (lazily imported) and a deterministic local "fake"
provider so the agent workflow runs without any external API key.
"""
from app.rag.llm.base import LLMProvider
from app.rag.llm.factory import get_llm_provider

__all__ = ["LLMProvider", "get_llm_provider"]
