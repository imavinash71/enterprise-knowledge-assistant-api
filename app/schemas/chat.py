"""Pydantic schemas for the ``Chat`` entity."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.agent import CitationOut
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


# --------------------------------------------------------------------------- #
# Chat API request/response DTOs
# --------------------------------------------------------------------------- #
class ChatRequest(BaseModel):
    """Payload for asking a question in a chat conversation."""

    question: str = Field(..., min_length=1)
    chat_id: int | None = Field(
        default=None,
        description="Continue an existing conversation; omit to start a new one.",
    )
    document_id: int | None = Field(
        default=None, description="Restrict retrieval to a single document."
    )
    top_k: int | None = Field(default=None, ge=1, le=50)


class ChatResponse(BaseModel):
    """The assistant's answer plus its grounding and confidence."""

    chat_id: int
    question: str
    answer: str
    intent: str
    confidence: float
    verified: bool
    sources: list[CitationOut]


class ChatHistory(BaseModel):
    """A user's conversations, most recent first, with their messages."""

    total: int
    items: list[ChatWithMessages]
