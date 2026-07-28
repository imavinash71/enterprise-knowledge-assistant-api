"""Repository for the ``Message`` entity."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.message import Message
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """Data-access operations for :class:`~app.models.message.Message`."""

    def __init__(self, db: Session) -> None:
        super().__init__(Message, db)
