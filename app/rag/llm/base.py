"""LLM provider strategy interface."""
from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Strategy for generating text completions from a prompt.

    The interface is deliberately minimal - a single :meth:`generate` call with
    an optional system instruction - so it maps cleanly onto any chat model
    while remaining easy to fake for tests.
    """

    @abstractmethod
    def generate(self, prompt: str, *, system: str | None = None) -> str:
        """Return the model's text response for ``prompt``.

        Args:
            prompt: The user/content prompt.
            system: Optional system instruction guiding the model's behavior.

        Returns:
            The generated text.
        """
        raise NotImplementedError
