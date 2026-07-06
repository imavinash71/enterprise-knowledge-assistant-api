"""Text chunking for the RAG pipeline.

Wraps LangChain's :class:`RecursiveCharacterTextSplitter` behind a small,
stable interface so the rest of the codebase does not depend on LangChain
internals and the splitter can be swapped later.
"""
from __future__ import annotations

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


class TextChunker:
    """Split long text into overlapping, semantically-aware chunks.

    Uses a recursive character splitter that tries increasingly fine separators
    (paragraphs, then lines, then words) to keep related text together while
    respecting the target chunk size.
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        self._chunk_size = chunk_size or settings.CHUNK_SIZE
        self._chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
            # Measure length in characters; keep separators out of chunk edges.
            length_function=len,
            is_separator_regex=False,
        )

    def split(self, text: str) -> list[str]:
        """Split ``text`` into a list of non-empty chunks."""
        if not text or not text.strip():
            return []
        return [chunk for chunk in self._splitter.split_text(text) if chunk.strip()]
