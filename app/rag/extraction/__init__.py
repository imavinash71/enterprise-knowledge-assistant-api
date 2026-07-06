"""Document text extraction package.

Implements the *strategy pattern* for pulling plain text out of different file
formats. Each :class:`~app.rag.extraction.base.TextExtractor` encapsulates the
logic for one family of extensions, and
:class:`~app.rag.extraction.service.DocumentProcessingService` selects the right
strategy at runtime. New formats are added by writing a new extractor and
registering it - no existing code needs to change (Open/Closed Principle).
"""
from app.rag.extraction.base import TextExtractor
from app.rag.extraction.service import DocumentProcessingService

__all__ = ["TextExtractor", "DocumentProcessingService"]
