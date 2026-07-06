"""PDF text extraction strategy."""
from __future__ import annotations

from io import BytesIO
from typing import ClassVar

from pypdf import PdfReader

from app.rag.extraction.base import TextExtractor


class PdfExtractor(TextExtractor):
    """Extract text from PDF documents using :mod:`pypdf`."""

    extensions: ClassVar[frozenset[str]] = frozenset({".pdf"})

    def extract(self, data: bytes) -> str:
        reader = PdfReader(BytesIO(data))
        # ``extract_text`` may return ``None`` for image-only pages.
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)
