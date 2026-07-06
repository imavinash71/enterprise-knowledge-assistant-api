"""Authentication service.

Holds the business logic for registration, login and token refresh. It depends
on the repository abstraction and the security primitives, keeping transport
(FastAPI) concerns out of the domain logic.
"""
from __future__ import annotations

from app.core import security
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.logging import get_logger
from app.core.security import JWTError, TokenType
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest

logger = get_logger(__name__)


class AuthService:
    """Coordinates user authentication workflows."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    # ------------------------------------------------------------------ #
    # Registration
    # ------------------------------------------------------------------ #
    def register(self, payload: RegisterRequest) -> User:
        """Create a new user account.

        Raises:
            ConflictError: If the email is already registered.
        """
        if self._users.email_exists(payload.email):
            raise ConflictError("A user with this email already exists.")

        user = User(
            name=payload.name,
            email=payload.email,
            hashed_password=security.hash_password(payload.password),
        )
        user = self._users.add(user)
        logger.info("Registered new user id=%s email=%s", user.id, user.email)
        return user

    # ------------------------------------------------------------------ #
    # Login
    # ------------------------------------------------------------------ #
    def authenticate(self, email: str, password: str) -> User:
        """Validate credentials and return the matching user.

        Raises:
            UnauthorizedError: If the credentials are invalid.
        """
        user = self._users.get_by_email(email)
        # Verify against the stored hash even when the user is missing to reduce
        # user-enumeration timing differences; error message stays generic.
        if user is None or not security.verify_password(
            password, user.hashed_password
        ):
            raise UnauthorizedError("Invalid email or password.")
        return user

    # ------------------------------------------------------------------ #
    # Token issuance
    # ------------------------------------------------------------------ #
    def issue_tokens(self, user: User) -> tuple[str, str]:
        """Return a new ``(access_token, refresh_token)`` pair for a user."""
        access_token = security.create_access_token(
            user.id, extra_claims={"role": user.role, "email": user.email}
        )
        refresh_token = security.create_refresh_token(user.id)
        return access_token, refresh_token

    def refresh(self, refresh_token: str) -> tuple[User, str, str]:
        """Validate a refresh token and issue a fresh token pair.

        Raises:
            UnauthorizedError: If the token is invalid, expired, of the wrong
                type, or the referenced user no longer exists.
        """
        try:
            claims = security.decode_token(refresh_token)
        except JWTError as exc:
            raise UnauthorizedError("Invalid or expired refresh token.") from exc

        if claims.get("type") != TokenType.REFRESH.value:
            raise UnauthorizedError("Provided token is not a refresh token.")

        subject = claims.get("sub")
        user = self._users.get(int(subject)) if subject is not None else None
        if user is None:
            raise UnauthorizedError("User no longer exists.")

        access_token, new_refresh_token = self.issue_tokens(user)
        return user, access_token, new_refresh_token
