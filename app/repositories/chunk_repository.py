"""Repository for the ``Chunk`` entity, including vector similarity search."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.repositories.base import BaseRepository


@dataclass(frozen=True)
class ScoredChunk:
    """A chunk paired with its similarity score (1.0 = identical)."""

    chunk: Chunk
    score: float


class ChunkRepository(BaseRepository[Chunk]):
    """Data-access operations for :class:`~app.models.chunk.Chunk`."""

    def __init__(self, db: Session) -> None:
        super().__init__(Chunk, db)

    def add_many(self, chunks: Sequence[Chunk]) -> list[Chunk]:
        """Bulk-insert chunks and flush the session."""
        self.db.add_all(chunks)
        self.db.flush()
        return list(chunks)

    def delete_by_document(self, document_id: int) -> int:
        """Delete all chunks belonging to a document; return the count removed."""
        stmt = delete(Chunk).where(Chunk.document_id == document_id)
        result = self.db.execute(stmt)
        return result.rowcount or 0

    def count_by_document(self, document_id: int) -> int:
        """Return the number of chunks stored for a document."""
        from sqlalchemy import func

        stmt = select(func.count(Chunk.id)).where(
            Chunk.document_id == document_id
        )
        return self.db.execute(stmt).scalar_one()

    def similarity_search(
        self,
        embedding: Sequence[float],
        *,
        top_k: int,
        owner_id: int | None = None,
        document_id: int | None = None,
    ) -> list[ScoredChunk]:
        """Return the ``top_k`` most similar chunks to ``embedding``.

        Uses pgvector's cosine distance for ranking. The returned ``score`` is
        cosine similarity (``1 - distance``), so higher is more similar.

        Args:
            embedding: The query vector.
            top_k: Maximum number of chunks to return.
            owner_id: If set, restrict results to documents owned by this user.
            document_id: If set, restrict results to a single document.
        """
        distance = Chunk.embedding.cosine_distance(embedding).label("distance")
        stmt = select(Chunk, distance).where(Chunk.embedding.isnot(None))

        # Join to documents only when we need to filter by ownership.
        if owner_id is not None:
            stmt = stmt.join(Document, Chunk.document_id == Document.id).where(
                Document.uploaded_by == owner_id
            )
        if document_id is not None:
            stmt = stmt.where(Chunk.document_id == document_id)

        stmt = stmt.order_by(distance).limit(top_k)

        rows = self.db.execute(stmt).all()
        return [
            ScoredChunk(chunk=row[0], score=1.0 - float(row[1])) for row in rows
        ]
