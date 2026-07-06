"""Document service.

Coordinates file storage and metadata persistence for uploaded documents. It
depends on the storage service (disk) and the document repository (database),
keeping transport concerns in the API layer.
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

from fastapi import UploadFile

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.logging import get_logger
from app.models.document import Document
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.storage_service import StorageService

logger = get_logger(__name__)


class DocumentService:
    """Business logic for uploading, listing and deleting documents."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        storage_service: StorageService,
    ) -> None:
        self._documents = document_repository
        self._storage = storage_service

    def upload(
        self,
        upload: UploadFile,
        *,
        owner: User,
        title: str | None = None,
    ) -> Document:
        """Persist an uploaded file and its metadata.

        The file is written to disk first; if the subsequent database insert
        fails, the orphaned file is removed to avoid leaking storage.

        Raises:
            BadRequestError: If the file fails validation (propagated from the
                storage service).
        """
        stored = self._storage.save(upload)
        try:
            document = Document(
                title=title or Path(stored.original_filename).stem,
                filename=stored.original_filename,
                file_path=stored.relative_path,
                file_size=stored.size,
                content_type=stored.content_type,
                uploaded_by=owner.id,
            )
            document = self._documents.add(document)
        except Exception:
            # Roll back the filesystem side-effect on any persistence failure.
            self._storage.delete(stored.relative_path)
            raise

        logger.info(
            "User id=%s uploaded document id=%s (%s)",
            owner.id,
            document.id,
            document.filename,
        )
        return document

    def list_for_user(
        self, owner: User, *, skip: int = 0, limit: int = 100
    ) -> tuple[int, Sequence[Document]]:
        """Return the total count and a page of the user's documents."""
        total = self._documents.count_by_user(owner.id)
        items = self._documents.list_by_user(owner.id, skip=skip, limit=limit)
        return total, items

    def get_owned(self, document_id: int, user: User) -> Document:
        """Return a document the user is allowed to access.

        Raises:
            NotFoundError: If the document does not exist.
            ForbiddenError: If the user neither owns the document nor is admin.
        """
        document = self._documents.get(document_id)
        if document is None:
            raise NotFoundError("Document not found.")
        if document.uploaded_by != user.id and user.role != UserRole.ADMIN.value:
            raise ForbiddenError("You do not have access to this document.")
        return document

    def delete(self, document_id: int, user: User) -> None:
        """Delete a document's metadata and its stored file.

        Raises:
            NotFoundError: If the document does not exist.
            ForbiddenError: If the user is not allowed to delete it.
        """
        document = self.get_owned(document_id, user)
        file_path = document.file_path
        self._documents.delete(document)
        # Remove the file after the row is staged for deletion; the endpoint
        # commits the transaction. Filesystem cleanup is best-effort.
        self._storage.delete(file_path)
        logger.info("User id=%s deleted document id=%s", user.id, document_id)
