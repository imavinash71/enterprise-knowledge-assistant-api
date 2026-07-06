"""Ingestion service: turn a stored document into searchable vector chunks.

Pipeline: read file -> extract text -> chunk -> embed -> persist. This service
composes the extraction, chunking, embedding and repository components, keeping
each responsibility in its own reusable unit (SRP).
"""
from __future__ import annotations

from pathlib import Path

from app.core.exceptions import UnprocessableEntityError
from app.core.logging import get_logger
from app.models.chunk import Chunk
from app.models.document import Document
from app.rag.chunking import TextChunker
from app.rag.embeddings.base import EmbeddingProvider
from app.rag.extraction.service import DocumentProcessingService
from app.repositories.chunk_repository import ChunkRepository
from app.services.storage_service import StorageService

logger = get_logger(__name__)


class IngestionService:
    """Extracts, chunks, embeds and stores a document's content."""

    def __init__(
        self,
        chunk_repository: ChunkRepository,
        storage_service: StorageService,
        processing_service: DocumentProcessingService,
        chunker: TextChunker,
        embedding_provider: EmbeddingProvider,
    ) -> None:
        self._chunks = chunk_repository
        self._storage = storage_service
        self._processing = processing_service
        self._chunker = chunker
        self._embeddings = embedding_provider

    def ingest(self, document: Document) -> int:
        """Ingest a document and return the number of chunks created.

        Existing chunks for the document are removed first so ingestion is
        idempotent and safe to re-run after a re-upload.

        Raises:
            UnprocessableEntityError: If no text can be extracted from the file.
        """
        data = self._storage.read(document.file_path)
        extension = Path(document.filename).suffix
        text = self._processing.extract_text(data, extension)

        if not text.strip():
            raise UnprocessableEntityError(
                "The document contains no extractable text to ingest."
            )

        pieces = self._chunker.split(text)
        if not pieces:
            raise UnprocessableEntityError(
                "The document produced no chunks to ingest."
            )

        # Replace any previous chunks for this document (idempotent re-ingest).
        self._chunks.delete_by_document(document.id)

        vectors = self._embeddings.embed_documents(pieces)
        chunks = [
            Chunk(document_id=document.id, content=piece, embedding=vector)
            for piece, vector in zip(pieces, vectors)
        ]
        self._chunks.add_many(chunks)

        logger.info(
            "Ingested document id=%s into %d chunks", document.id, len(chunks)
        )
        return len(chunks)
