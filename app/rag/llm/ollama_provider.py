"""Ollama LLM provider.

Talks to a self-hosted or remote `Ollama <https://ollama.com>`_ server over its
HTTP ``/api/generate`` endpoint. No API key is required — only a reachable base
URL (see ``OLLAMA_BASE_URL``). Streaming responses are consumed and accumulated
into a single string to satisfy the synchronous :meth:`generate` contract.
"""
from __future__ import annotations

import json

from app.core.config import settings
from app.core.exceptions import AppException
from app.rag.llm.base import LLMProvider


class OllamaLLMProvider(LLMProvider):
    """Text generation backed by an Ollama server's ``/api/generate`` endpoint.

    The ``requests`` import is deferred to call time so importing this module
    never requires the dependency unless the provider is actually used.
    """

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        temperature: float | None = None,
        timeout: float | None = None,
    ) -> None:
        # Prefer the dedicated OLLAMA_MODEL; fall back to LLM_MODEL only when it
        # isn't an obvious cloud model name (gpt-*, gemini-*).
        configured = model or settings.OLLAMA_MODEL or settings.LLM_MODEL
        self._model = configured
        self._base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self._temperature = (
            settings.LLM_TEMPERATURE if temperature is None else temperature
        )
        self._timeout = settings.OLLAMA_TIMEOUT if timeout is None else timeout

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        try:
            import requests
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise AppException(
                "The 'requests' package is required for the Ollama LLM provider."
            ) from exc

        url = f"{self._base_url}/api/generate"
        payload: dict[str, object] = {
            "model": self._model,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": self._temperature},
        }
        if system:
            payload["system"] = system

        parts: list[str] = []
        try:
            with requests.post(
                url, json=payload, stream=True, timeout=self._timeout
            ) as response:
                response.raise_for_status()
                # Ollama streams newline-delimited JSON objects; accumulate the
                # incremental ``response`` fields until ``done`` is signalled.
                for line in response.iter_lines():
                    if not line:
                        continue
                    data = json.loads(line.decode("utf-8"))
                    if "response" in data:
                        parts.append(data["response"])
                    if data.get("done"):
                        break
        except requests.exceptions.RequestException as exc:
            raise AppException(
                f"Ollama request to {url} failed: {exc}",
                error_code="llm_provider_error",
            ) from exc

        return "".join(parts).strip()
