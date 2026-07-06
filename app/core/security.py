"""Security primitives: password hashing and JWT token handling.

This module centralizes all cryptographic concerns so the rest of the codebase
depends on a small, well-defined surface (SRP). It exposes:

* password hashing / verification via passlib (bcrypt)
* creation of signed JWT access and refresh tokens
* decoding / validation of JWTs
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt is the industry standard for password hashing; passlib manages salting
# and lets us transparently upgrade the scheme later.
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenType(str, Enum):
    """Discriminates access tokens from refresh tokens via the ``type`` claim."""

    ACCESS = "access"
    REFRESH = "refresh"


# --------------------------------------------------------------------------- #
# Password hashing
# --------------------------------------------------------------------------- #
def hash_password(password: str) -> str:
    """Return a bcrypt hash for the given plaintext password."""
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return ``True`` if the plaintext password matches the stored hash."""
    return _pwd_context.verify(plain_password, hashed_password)


# --------------------------------------------------------------------------- #
# JWT tokens
# --------------------------------------------------------------------------- #
def _create_token(
    subject: str | int,
    token_type: TokenType,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Build and sign a JWT with standard registered claims."""
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(
    subject: str | int,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a short-lived access token for the given subject (user id)."""
    return _create_token(
        subject,
        TokenType.ACCESS,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims,
    )


def create_refresh_token(subject: str | int) -> str:
    """Create a long-lived refresh token for the given subject (user id)."""
    return _create_token(
        subject,
        TokenType.REFRESH,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT, returning its claims.

    Raises:
        JWTError: If the token is malformed, expired, or has an invalid
            signature. Callers are expected to translate this into an
            application-level ``UnauthorizedError``.
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


__all__ = [
    "TokenType",
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "JWTError",
]
