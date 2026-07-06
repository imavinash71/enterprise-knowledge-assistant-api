"""Pydantic schemas for the ``Document`` entity."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    """Shared document fields."""

    title: str = Field(..., max_length=512)
    filename: str = Field(..., max_length=512)


class DocumentCreate(DocumentBase):
    """Payload for registering an uploaded document.

    ``uploaded_by`` is typically derived from the authenticated user rather than
    the request body, but is accepted here for flexibility in service calls.
    """

    uploaded_by: int


class DocumentRead(DocumentBase):
    """Document representation returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    uploaded_by: int
    upload_date: datetime
