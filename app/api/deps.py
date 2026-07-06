"""Shared API dependencies.

Central place for FastAPI dependency-injection providers: the database session,
repositories, services, and the current-authenticated-user resolvers. Endpoints
import everything they need from here.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import JWTError, TokenType, decode_token
from app.database.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

# ``tokenUrl`` powers the Swagger "Authorize" button; it points at the login
# endpoint that returns a bearer token.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login", auto_error=False
)

DbSession = Annotated[Session, Depends(get_db)]


# --------------------------------------------------------------------------- #
# Repository / service providers
# --------------------------------------------------------------------------- #
def get_user_repository(db: DbSession) -> UserRepository:
    """Provide a :class:`UserRepository` bound to the request session."""
    return UserRepository(db)


def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    """Provide an :class:`AuthService` with its dependencies injected."""
    return AuthService(user_repository)


# --------------------------------------------------------------------------- #
# Current user resolution
# --------------------------------------------------------------------------- #
def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    """Resolve and return the authenticated user from a bearer access token.

    Raises:
        UnauthorizedError: If the token is missing, invalid, expired, of the
            wrong type, or references a non-existent user.
    """
    if not token:
        raise UnauthorizedError("Not authenticated.")

    try:
        claims = decode_token(token)
    except JWTError as exc:
        raise UnauthorizedError("Could not validate credentials.") from exc

    if claims.get("type") != TokenType.ACCESS.value:
        raise UnauthorizedError("Provided token is not an access token.")

    subject = claims.get("sub")
    user = user_repository.get(int(subject)) if subject is not None else None
    if user is None:
        raise UnauthorizedError("User no longer exists.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*roles: UserRole):
    """Build a dependency that authorizes only the given user roles.

    Usage::

        @router.get("/admin", dependencies=[Depends(require_role(UserRole.ADMIN))])
    """
    allowed = {role.value for role in roles}

    def _guard(current_user: CurrentUser) -> User:
        if current_user.role not in allowed:
            raise ForbiddenError("You do not have access to this resource.")
        return current_user

    return _guard


__all__ = [
    "DbSession",
    "CurrentUser",
    "get_db",
    "get_user_repository",
    "get_auth_service",
    "get_current_user",
    "require_role",
]
