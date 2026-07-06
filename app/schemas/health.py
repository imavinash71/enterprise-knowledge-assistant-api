"""Schemas for the health endpoint."""
from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response model for the health check endpoint."""

    status: str
    service: str
    version: str
    environment: str
