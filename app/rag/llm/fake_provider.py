"""Deterministic local LLM provider (no external API).

Produces stable, rule-based responses so the LangGraph workflow is fully
runnable and testable without an API key. It recognizes lightweight task tags
placed at the start of the system instruction by the agent nodes:

* ``[TASK:intent]``    - classify the user's message into an intent label.
* ``[TASK:answer]``    - answer using numbered ``[n]`` sources in the prompt.
* ``[TASK:smalltalk]`` - produce a short conversational reply.

Real providers ignore these tags (they are harmless text), so nodes can share
one prompt format across providers. This provider is NOT semantically
intelligent and must not be relied upon for production answer quality.
"""
from __future__ import annotations

import re

from app.rag.llm.base import LLMProvider

# Extracts numbered source blocks like "[1] some text" up to the next marker.
_SOURCE_RE = re.compile(r"\[(\d+)\]\s*(.*?)(?=\n\[\d+\]|\Z)", re.DOTALL)

_GREETING_WORDS = ("hello", "hi", "hey", "good morning", "good evening", "thanks")
_QUESTION_WORDS = ("what", "who", "when", "where", "why", "how", "which", "list", "explain")


class FakeLLMProvider(LLMProvider):
    """Rule-based, deterministic LLM stand-in for development and testing."""

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        tag = (system or "").strip().lower()

        if tag.startswith("[task:intent]"):
            return self._classify_intent(prompt)
        if tag.startswith("[task:smalltalk]"):
            return "Hello! I'm your knowledge assistant. Ask me about your documents."
        # Default: answer generation.
        return self._generate_answer(prompt)

    # ------------------------------------------------------------------ #
    # Task implementations
    # ------------------------------------------------------------------ #
    def _classify_intent(self, prompt: str) -> str:
        text = prompt.lower()
        if any(word in text for word in _GREETING_WORDS) and "?" not in text:
            return "greeting"
        if "?" in text or any(text.startswith(w) for w in _QUESTION_WORDS):
            return "knowledge_query"
        if any(word in text for word in _QUESTION_WORDS):
            return "knowledge_query"
        return "chitchat"

    def _generate_answer(self, prompt: str) -> str:
        sources = _SOURCE_RE.findall(prompt)
        if not sources:
            return (
                "I could not find relevant information in the provided documents "
                "to answer this question."
            )
        # Build a concise answer that cites the first one or two sources so the
        # citation verifier has real references to validate.
        first_idx, first_text = sources[0]
        snippet = " ".join(first_text.split())[:200]
        answer = f"Based on the available documents, {snippet} [{first_idx}]."
        if len(sources) > 1:
            second_idx = sources[1][0]
            answer += f" Additional context supports this [{second_idx}]."
        return answer
