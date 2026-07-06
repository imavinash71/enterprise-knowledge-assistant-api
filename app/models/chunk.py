"""Chunk ORM model (document fragment + embedding vector)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.database.base_class import Base

if TYPE_CHECKING:
    from app.models.document import Document


class Chunk(Base):
    """A chunk of a document together with its embedding vector.

    The ``embedding`` column uses pgvector's ``Vector`` type; its dimension is
    driven by ``settings.EMBEDDING_DIM`` so it stays aligned with the embedding
    model in use.
    """

    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(settings.EMBEDDING_DIM), nullable=True
    )

    # Relationships ----------------------------------------------------- #
    document: Mapped["Document"] = relationship(back_populates="chunks")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Chunk id={self.id} document_id={self.document_id}>"
