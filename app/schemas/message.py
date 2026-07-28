"""Pydantic schemas for the ``Message`` entity."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import MessageRole
from app.schemas.agent import CitationOut


class MessageBase(BaseModel):
    """Shared message fields."""

    role: MessageRole
    message: str


class MessageCreate(MessageBase):
    """Payload for creating a message within a chat."""

    chat_id: int


class MessageRead(MessageBase):
    """Message representation returned to clients.

    ``sources`` and ``confidence`` are populated only for assistant answers.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    timestamp: datetime
    sources: list[CitationOut] | None = None
    confidence: float | None = None
