"""Filesystem storage service for uploaded files.

Encapsulates all disk I/O and validation so higher layers deal only with
domain concepts. Keeping this separate from the database-oriented
``DocumentService`` follows the Single Responsibility Principle and makes the
storage backend easy to swap (e.g. S3) later.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import BadRequestError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Read/stream the upload in fixed-size chunks to bound memory usage.
_CHUNK_SIZE = 1024 * 1024  # 1 MiB


@dataclass(frozen=True)
class StoredFile:
    """Metadata describing a file that was persisted to disk."""

    original_filename: str
    stored_filename: str
    relative_path: str
    absolute_path: Path
    size: int
    content_type: str | None


class StorageService:
    """Validates and persists uploaded files under the configured directory."""

    def __init__(self) -> None:
        self._base_dir = Path(settings.UPLOAD_DIR)
        self._allowed_extensions = settings.allowed_upload_extensions
        self._max_size = settings.max_upload_size_bytes

    # ------------------------------------------------------------------ #
    # Validation
    # ------------------------------------------------------------------ #
    def _validate_extension(self, filename: str) -> str:
        """Return the validated, lower-cased file extension.

        Raises:
            BadRequestError: If the filename has no extension or an unsupported
                one.
        """
        suffix = Path(filename).suffix.lower()
        if not suffix:
            raise BadRequestError("Uploaded file has no extension.")
        if suffix not in self._allowed_extensions:
            allowed = ", ".join(sorted(self._allowed_extensions))
            raise BadRequestError(
                f"Unsupported file type '{suffix}'. Allowed types: {allowed}."
            )
        return suffix

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #
    def save(self, upload: UploadFile) -> StoredFile:
        """Validate and stream an uploaded file to disk.

        The file is streamed in chunks and aborted (with cleanup) if it exceeds
        the configured maximum size, so oversized uploads never fully land on
        disk.

        Raises:
            BadRequestError: If the file is empty, has an invalid extension, or
                exceeds the maximum allowed size.
        """
        original_filename = upload.filename or "upload"
        suffix = self._validate_extension(original_filename)

        # Randomized stored name avoids collisions and path-traversal issues
        # from user-controlled filenames.
        stored_filename = f"{uuid.uuid4().hex}{suffix}"
        self._base_dir.mkdir(parents=True, exist_ok=True)
        absolute_path = self._base_dir / stored_filename

        size = 0
        try:
            with absolute_path.open("wb") as buffer:
                while chunk := upload.file.read(_CHUNK_SIZE):
                    size += len(chunk)
                    if size > self._max_size:
                        raise BadRequestError(
                            "File exceeds the maximum allowed size of "
                            f"{settings.MAX_UPLOAD_SIZE_MB} MB."
                        )
                    buffer.write(chunk)
        except BadRequestError:
            absolute_path.unlink(missing_ok=True)
            raise
        except OSError as exc:  # pragma: no cover - filesystem failure
            absolute_path.unlink(missing_ok=True)
            logger.exception("Failed to write uploaded file: %s", exc)
            raise
        finally:
            upload.file.close()

        if size == 0:
            absolute_path.unlink(missing_ok=True)
            raise BadRequestError("Uploaded file is empty.")

        logger.info(
            "Stored upload %r as %s (%d bytes)",
            original_filename,
            stored_filename,
            size,
        )
        return StoredFile(
            original_filename=original_filename,
            stored_filename=stored_filename,
            relative_path=stored_filename,
            absolute_path=absolute_path,
            size=size,
            content_type=upload.content_type,
        )

    def delete(self, relative_path: str) -> None:
        """Remove a stored file if it exists (idempotent)."""
        target = self._base_dir / relative_path
        try:
            target.unlink(missing_ok=True)
        except OSError as exc:  # pragma: no cover - filesystem failure
            logger.warning("Could not delete file %s: %s", target, exc)

    def read(self, relative_path: str) -> bytes:
        """Return the raw bytes of a stored file.

        Raises:
            FileNotFoundError: If the file does not exist on disk.
        """
        return (self._base_dir / relative_path).read_bytes()
