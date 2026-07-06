"""Repository for the ``Document`` entity."""
from __future__ import annotations

from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Data-access operations for :class:`~app.models.document.Document`."""

    def __init__(self, db: Session) -> None:
        super().__init__(Document, db)

    def list_by_user(
        self, user_id: int, *, skip: int = 0, limit: int = 100
    ) -> Sequence[Document]:
        """Return a user's documents, most recent first."""
        stmt = (
            select(Document)
            .where(Document.uploaded_by == user_id)
            .order_by(Document.upload_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.db.execute(stmt).scalars().all()

    def count_by_user(self, user_id: int) -> int:
        """Return the total number of documents owned by a user."""
        stmt = select(func.count(Document.id)).where(
            Document.uploaded_by == user_id
        )
        return self.db.execute(stmt).scalar_one()
