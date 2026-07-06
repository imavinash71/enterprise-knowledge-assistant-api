"""Pydantic schemas for the ``Chat`` entity."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.message import MessageRead


class ChatBase(BaseModel):
    """Shared chat fields."""

    title: str = Field(..., max_length=512)


class ChatCreate(ChatBase):
    """Payload for creating a chat.

    ``user_id`` is typically taken from the authenticated user rather than the
    request body, but is accepted here for flexibility in service calls.
    """

    user_id: int


class ChatUpdate(BaseModel):
    """Payload for partially updating a chat."""

    title: str | None = Field(default=None, max_length=512)


class ChatRead(ChatBase):
    """Chat representation returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class ChatWithMessages(ChatRead):
    """Chat representation including its ordered messages."""

    messages: list[MessageRead] = []
