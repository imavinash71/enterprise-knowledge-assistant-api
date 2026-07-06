"""Enumerations shared across ORM models and schemas.

Defined as ``str``-based enums so values serialize cleanly to JSON and can be
stored as plain ``VARCHAR`` columns. We intentionally avoid native PostgreSQL
ENUM types to keep migrations simple and allow roles to evolve without a
schema change.
"""
from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    """Application-level user roles."""

    ADMIN = "admin"
    USER = "user"


class MessageRole(str, Enum):
    """Author of a chat message, aligned with LLM chat conventions."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
