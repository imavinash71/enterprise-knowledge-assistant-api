"""Authentication endpoints: register, login, refresh, and current user."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, DbSession, get_auth_service
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(
    payload: RegisterRequest,
    db: DbSession,
    auth_service: AuthServiceDep,
) -> AuthResponse:
    """Create an account and return an authenticated token pair."""
    user = auth_service.register(payload)
    access_token, refresh_token = auth_service.issue_tokens(user)
    # Commit the transaction at the API boundary once the unit of work succeeds.
    db.commit()
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Log in with email and password",
)
def login(
    payload: LoginRequest,
    auth_service: AuthServiceDep,
) -> AuthResponse:
    """Authenticate a user and return a token pair with the user profile."""
    user = auth_service.authenticate(payload.email, payload.password)
    access_token, refresh_token = auth_service.issue_tokens(user)
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access and refresh tokens",
)
def refresh(
    payload: RefreshRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    """Exchange a valid refresh token for a new token pair (rotation)."""
    _, access_token, refresh_token = auth_service.refresh(payload.refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the current authenticated user",
)
def read_current_user(current_user: CurrentUser) -> UserRead:
    """Return the profile of the authenticated user (protected route)."""
    return UserRead.model_validate(current_user)
