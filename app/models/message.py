"""Message ORM model."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base
from app.models.enums import MessageRole

if TYPE_CHECKING:
    from app.models.chat import Chat


class Message(Base):
    """A single message within a chat conversation."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # Stored as VARCHAR; validated against ``MessageRole`` at the schema layer.
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # Assistant-only answer metadata. ``sources`` holds the retrieved chunks
    # that grounded the answer and ``confidence`` the agent's self-assessed
    # score; both are NULL for user/system messages.
    sources: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSONB, nullable=True
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships ----------------------------------------------------- #
    chat: Mapped["Chat"] = relationship(back_populates="messages")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Message id={self.id} chat_id={self.chat_id} role={self.role!r}>"
