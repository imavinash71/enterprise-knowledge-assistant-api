"""Plain-text extraction strategy."""
from __future__ import annotations

from typing import ClassVar

from app.rag.extraction.base import TextExtractor


class TxtExtractor(TextExtractor):
    """Decode plain ``.txt`` files.

    Tries UTF-8 first (the common case) and falls back to a permissive decode
    so that files in other encodings still yield usable text instead of raising.
    """

    extensions: ClassVar[frozenset[str]] = frozenset({".txt"})

    def extract(self, data: bytes) -> str:
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            # Latin-1 maps every byte to a character, guaranteeing no failure.
            return data.decode("latin-1", errors="replace")
