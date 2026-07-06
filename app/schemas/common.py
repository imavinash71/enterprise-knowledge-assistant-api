"""Common, reusable Pydantic schemas."""
from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ORMModel(BaseModel):
    """Base schema for models read from the ORM."""

    model_config = {"from_attributes": True}


class Message(BaseModel):
    """Generic message response."""

    message: str


class ErrorDetail(BaseModel):
    """Structured error payload returned by exception handlers."""

    code: str
    message: str
    details: object | None = None


class ErrorResponse(BaseModel):
    """Envelope wrapping an :class:`ErrorDetail`."""

    error: ErrorDetail
