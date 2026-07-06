"""Generic base repository implementing common CRUD operations."""
from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Reusable CRUD repository parameterized by an ORM model type.

    Concrete repositories subclass this and add entity-specific queries. The
    repository owns *how* data is fetched/persisted; it does not commit unless
    explicitly asked, leaving transaction boundaries to the service layer.
    """

    def __init__(self, model: type[ModelType], db: Session) -> None:
        self.model = model
        self.db = db

    def get(self, id: int) -> ModelType | None:
        """Return an entity by primary key, or ``None`` if not found."""
        return self.db.get(self.model, id)

    def list(self, *, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Return a paginated list of entities."""
        stmt = select(self.model).offset(skip).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def add(self, entity: ModelType) -> ModelType:
        """Stage a new entity and flush to obtain its generated primary key."""
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        """Stage an entity for deletion."""
        self.db.delete(entity)
