"""OpenAI chat LLM provider."""
from __future__ import annotations

from functools import cached_property

from app.core.config import settings
from app.core.exceptions import AppException
from app.rag.llm.base import LLMProvider


class OpenAILLMProvider(LLMProvider):
    """Text generation backed by the OpenAI Chat Completions API.

    The client is created lazily so importing this module never requires the
    ``openai`` package or an API key unless the provider is actually used.
    """

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        temperature: float | None = None,
    ) -> None:
        self._model = model or settings.LLM_MODEL
        self._api_key = api_key or settings.OPENAI_API_KEY
        self._temperature = (
            settings.LLM_TEMPERATURE if temperature is None else temperature
        )

    @cached_property
    def _client(self):
        if not self._api_key:
            raise AppException(
                "OPENAI_API_KEY is not configured.", error_code="config_error"
            )
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise AppException(
                "The 'openai' package is required for the OpenAI LLM provider."
            ) from exc
        return OpenAI(api_key=self._api_key)

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
        )
        return (response.choices[0].message.content or "").strip()
