"""Authentication request/response schemas."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    """Payload for registering a new account."""

    name: str = Field(..., max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Payload for logging in with email and password."""

    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    """Payload for exchanging a refresh token for new tokens."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Issued token pair returned to the client."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(TokenResponse):
    """Token pair plus the authenticated user's profile."""

    user: UserRead


class TokenPayload(BaseModel):
    """Decoded JWT claims we rely on."""

    sub: str
    type: str
    exp: int | None = None
    iat: int | None = None
