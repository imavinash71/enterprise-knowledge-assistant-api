"""Pydantic schemas for the ``Document`` entity."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    """Shared document fields."""

    title: str = Field(..., max_length=512)
    filename: str = Field(..., max_length=512)


class DocumentCreate(DocumentBase):
    """Internal payload for persisting an uploaded document's metadata.

    ``uploaded_by`` is derived from the authenticated user by the service layer;
    it is not accepted from the client request body.
    """

    file_path: str = Field(..., max_length=1024)
    file_size: int = Field(..., ge=0)
    content_type: str | None = Field(default=None, max_length=255)
    uploaded_by: int


class DocumentRead(DocumentBase):
    """Document representation returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    file_size: int
    content_type: str | None = None
    uploaded_by: int
    upload_date: datetime


class DocumentList(BaseModel):
    """Paginated collection of documents."""

    total: int
    items: list[DocumentRead]
