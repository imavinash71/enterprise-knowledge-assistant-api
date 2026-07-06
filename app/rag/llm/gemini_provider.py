"""Google Gemini LLM provider."""
from __future__ import annotations

from app.core.config import settings
from app.core.exceptions import AppException
from app.rag.llm.base import LLMProvider

_DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"


class GeminiLLMProvider(LLMProvider):
    """Text generation backed by Google's Generative AI (Gemini) API."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        temperature: float | None = None,
    ) -> None:
        # ``LLM_MODEL`` may hold an OpenAI-style name; fall back to a Gemini
        # default when it does not look like a Gemini model.
        configured = model or settings.LLM_MODEL
        self._model = configured if configured.startswith("gemini") else _DEFAULT_GEMINI_MODEL
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._temperature = (
            settings.LLM_TEMPERATURE if temperature is None else temperature
        )
        self._configured = False

    def _ensure_configured(self):
        if self._configured:
            return
        if not self._api_key:
            raise AppException(
                "GEMINI_API_KEY is not configured.", error_code="config_error"
            )
        try:
            import google.generativeai as genai
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise AppException(
                "The 'google-generativeai' package is required for the Gemini "
                "LLM provider."
            ) from exc
        genai.configure(api_key=self._api_key)
        self._genai = genai
        self._configured = True

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        self._ensure_configured()
        model = self._genai.GenerativeModel(
            self._model,
            system_instruction=system,
            generation_config={"temperature": self._temperature},
        )
        response = model.generate_content(prompt)
        return (response.text or "").strip()
