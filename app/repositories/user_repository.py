"""Repository for the ``User`` entity."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data-access operations for :class:`~app.models.user.User`."""

    def __init__(self, db: Session) -> None:
        super().__init__(User, db)

    def get_by_email(self, email: str) -> User | None:
        """Return the user with the given email, or ``None``."""
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def email_exists(self, email: str) -> bool:
        """Return ``True`` if a user with the given email already exists."""
        stmt = select(User.id).where(User.email == email)
        return self.db.execute(stmt).first() is not None
