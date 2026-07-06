"""Import target that exposes ``Base`` and all models to Alembic.

Import your model modules here so that Alembic autogenerate can detect them,
e.g. ``from app.models.document import Document  # noqa: F401``.
"""
from __future__ import annotations

from app.database.base_class import Base  # noqa: F401

# Import ORM models below so they are registered on ``Base.metadata``.
# from app.models.example import Example  # noqa: F401
