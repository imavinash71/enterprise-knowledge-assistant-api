"""Custom Starlette/FastAPI middleware."""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.security import JWTError, TokenType, decode_token


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Populate ``request.state`` with lightweight auth context.

    This middleware is intentionally *non-enforcing*: it decodes a bearer access
    token when present and stashes the resulting claims on the request so that
    downstream concerns (e.g. logging, tracing) can access the caller identity.
    Actual route protection is handled by the ``get_current_user`` dependency,
    which keeps authorization explicit and testable per-endpoint.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request.state.user_id = None
        request.state.token_claims = None

        authorization = request.headers.get("Authorization")
        if authorization and authorization.lower().startswith("bearer "):
            token = authorization.split(" ", 1)[1].strip()
            try:
                claims = decode_token(token)
                if claims.get("type") == TokenType.ACCESS.value:
                    request.state.user_id = claims.get("sub")
                    request.state.token_claims = claims
            except JWTError:
                # Invalid tokens are ignored here; enforcement happens in the
                # dependency layer so unauthenticated requests still reach public
                # routes normally.
                pass

        return await call_next(request)
