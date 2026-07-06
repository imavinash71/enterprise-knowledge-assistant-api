"""Document processing service: strategy selection + text cleaning.

This service is the public entry point for turning a document's bytes into
clean, normalized text. It holds a registry of
:class:`~app.rag.extraction.base.TextExtractor` strategies keyed by file
extension and delegates to the appropriate one at runtime.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from app.core.exceptions import UnprocessableEntityError
from app.core.logging import get_logger
from app.rag.extraction.base import TextExtractor
from app.rag.extraction.docx import DocxExtractor
from app.rag.extraction.pdf import PdfExtractor
from app.rag.extraction.pptx import PptxExtractor
from app.rag.extraction.txt import TxtExtractor
from app.utils.text import clean_text

logger = get_logger(__name__)


def _default_extractors() -> list[TextExtractor]:
    """Return the built-in extraction strategies."""
    return [PdfExtractor(), DocxExtractor(), TxtExtractor(), PptxExtractor()]


class DocumentProcessingService:
    """Extracts and cleans text from documents using pluggable strategies."""

    def __init__(self, extractors: Iterable[TextExtractor] | None = None) -> None:
        # Map each supported extension to its strategy for O(1) lookup.
        self._registry: dict[str, TextExtractor] = {}
        for extractor in extractors if extractors is not None else _default_extractors():
            self.register(extractor)

    # ------------------------------------------------------------------ #
    # Registry management
    # ------------------------------------------------------------------ #
    def register(self, extractor: TextExtractor) -> None:
        """Register an extraction strategy for all extensions it supports.

        A later registration for the same extension overrides the earlier one,
        which allows callers to swap in a custom implementation.
        """
        for extension in extractor.extensions:
            self._registry[extension.lower()] = extractor

    @property
    def supported_extensions(self) -> frozenset[str]:
        """Return the set of extensions the service can currently process."""
        return frozenset(self._registry)

    def _get_extractor(self, extension: str) -> TextExtractor:
        extractor = self._registry.get(extension.lower())
        if extractor is None:
            supported = ", ".join(sorted(self._registry))
            raise UnprocessableEntityError(
                f"No extractor registered for '{extension}'. "
                f"Supported types: {supported}."
            )
        return extractor

    # ------------------------------------------------------------------ #
    # Extraction
    # ------------------------------------------------------------------ #
    def extract_text(self, data: bytes, extension: str) -> str:
        """Extract and clean text from raw bytes for the given extension.

        Args:
            data: The document's raw bytes.
            extension: File extension including the leading dot (e.g. ``.pdf``).

        Returns:
            Cleaned, normalized text.

        Raises:
            UnprocessableEntityError: If the extension is unsupported or the
                document cannot be parsed.
        """
        extractor = self._get_extractor(extension)
        try:
            raw_text = extractor.extract(data)
        except UnprocessableEntityError:
            raise
        except Exception as exc:  # noqa: BLE001 - normalize all parse failures
            logger.exception("Failed to extract text from %s file", extension)
            raise UnprocessableEntityError(
                f"Could not extract text from the {extension} document."
            ) from exc

        return clean_text(raw_text)

    def extract_from_file(self, path: str | Path) -> str:
        """Read a file from disk and return its cleaned text.

        Args:
            path: Filesystem path to the document.

        Raises:
            UnprocessableEntityError: If the file type is unsupported or parsing
                fails.
        """
        file_path = Path(path)
        data = file_path.read_bytes()
        return self.extract_text(data, file_path.suffix)
