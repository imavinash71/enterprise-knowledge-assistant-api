"""Custom application exceptions."""
from __future__ import annotations

from typing import Any


class AppException(Exception):
    """Base class for all application-specific exceptions.

    Attributes:
        message: Human-readable error message.
        status_code: HTTP status code to return to the client.
        error_code: Stable machine-readable error identifier.
        details: Optional structured error context.
    """

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        *,
        status_code: int | None = None,
        error_code: str | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        self.details = details


class NotFoundError(AppException):
    """Raised when a requested resource does not exist."""

    status_code = 404
    error_code = "not_found"


class BadRequestError(AppException):
    """Raised when the client sends an invalid request."""

    status_code = 400
    error_code = "bad_request"


class UnauthorizedError(AppException):
    """Raised when authentication is required or has failed."""

    status_code = 401
    error_code = "unauthorized"


class ForbiddenError(AppException):
    """Raised when the client lacks permission for an action."""

    status_code = 403
    error_code = "forbidden"


class ConflictError(AppException):
    """Raised when a request conflicts with the current state."""

    status_code = 409
    error_code = "conflict"
