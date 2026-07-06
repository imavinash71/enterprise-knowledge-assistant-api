"""Document ORM model."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base

if TYPE_CHECKING:
    from app.models.chunk import Chunk
    from app.models.user import User


class Document(Base):
    """A source document uploaded by a user for knowledge retrieval."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    # Relative path (under the upload directory) of the stored file on disk.
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    # Size of the stored file in bytes.
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    # MIME type reported by the client (best-effort; may be ``None``).
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    upload_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships ----------------------------------------------------- #
    uploader: Mapped["User"] = relationship(back_populates="documents")
    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Document id={self.id} title={self.title!r}>"
