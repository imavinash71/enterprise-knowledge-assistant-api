"""Pydantic schemas for the ``User`` entity."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import UserRole


class UserBase(BaseModel):
    """Shared user fields."""

    name: str = Field(..., max_length=255)
    email: EmailStr
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    """Payload for registering a new user."""

    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Payload for partially updating a user."""

    name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    role: UserRole | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserRead(UserBase):
    """User representation returned to clients (never exposes the password)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
