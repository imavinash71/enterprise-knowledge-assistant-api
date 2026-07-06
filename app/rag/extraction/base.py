"""Strategy interface for text extraction."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar


class TextExtractor(ABC):
    """Base strategy for extracting plain text from a document's bytes.

    Concrete extractors declare the file extensions they support via
    :attr:`extensions` and implement :meth:`extract`. Working on raw ``bytes``
    (rather than a filesystem path) keeps strategies decoupled from the storage
    backend, so the same code works for local files, uploads, or object storage.
    """

    #: Lower-cased extensions (including the leading dot) this strategy handles.
    extensions: ClassVar[frozenset[str]] = frozenset()

    def supports(self, extension: str) -> bool:
        """Return ``True`` if this strategy handles the given extension."""
        return extension.lower() in self.extensions

    @abstractmethod
    def extract(self, data: bytes) -> str:
        """Extract and return raw (uncleaned) text from ``data``.

        Args:
            data: The raw bytes of the document.

        Returns:
            The extracted text. Cleaning/normalization is applied by the
            calling service, not by individual strategies.

        Raises:
            Exception: Implementations may raise on malformed input; the service
                layer translates these into an application-level error.
        """
        raise NotImplementedError
