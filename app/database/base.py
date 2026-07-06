"""Import target that exposes ``Base`` and all models to Alembic.

Import your model modules here so that Alembic autogenerate can detect them,
e.g. ``from app.models.document import Document  # noqa: F401``.
"""
from __future__ import annotations

from app.database.base_class import Base  # noqa: F401

# Import ORM models so they are registered on ``Base.metadata`` for Alembic.
from app.models import (  # noqa: F401
    Chat,
    Chunk,
    Document,
    Message,
    User,
)
