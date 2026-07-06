"""Shared API dependencies.

Re-exports common dependencies (such as the database session) so endpoints can
import everything they need from a single location.
"""
from __future__ import annotations

from app.database.session import get_db

__all__ = ["get_db"]
