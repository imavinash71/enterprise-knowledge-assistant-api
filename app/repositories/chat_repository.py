"""Repository for the ``Chat`` entity and its messages."""
from __future__ import annotations

from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.chat import Chat
from app.repositories.base import BaseRepository


class ChatRepository(BaseRepository[Chat]):
    """Data-access operations for :class:`~app.models.chat.Chat`."""

    def __init__(self, db: Session) -> None:
        super().__init__(Chat, db)

    def list_by_user(
        self, user_id: int, *, skip: int = 0, limit: int = 100
    ) -> Sequence[Chat]:
        """Return a user's chats (with messages eager-loaded), newest first."""
        stmt = (
            select(Chat)
            .where(Chat.user_id == user_id)
            .options(selectinload(Chat.messages))
            .order_by(Chat.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.db.execute(stmt).scalars().all()

    def count_by_user(self, user_id: int) -> int:
        """Return the total number of chats owned by a user."""
        stmt = select(func.count(Chat.id)).where(Chat.user_id == user_id)
        return self.db.execute(stmt).scalar_one()

    def get_with_messages(self, chat_id: int) -> Chat | None:
        """Return a chat with its ordered messages eager-loaded."""
        stmt = (
            select(Chat)
            .where(Chat.id == chat_id)
            .options(selectinload(Chat.messages))
        )
        return self.db.execute(stmt).scalar_one_or_none()
