"""Declarative base for SQLAlchemy ORM models."""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class that all ORM models inherit from."""

    pass
