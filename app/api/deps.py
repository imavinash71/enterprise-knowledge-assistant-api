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
from app.rag.chunking import TextChunker
from app.rag.embeddings import EmbeddingProvider, get_embedding_provider
from app.rag.extraction.service import DocumentProcessingService
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.document_service import DocumentService
from app.services.ingestion_service import IngestionService
from app.services.retrieval_service import RetrievalService
from app.services.storage_service import StorageService

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


def get_document_repository(db: DbSession) -> DocumentRepository:
    """Provide a :class:`DocumentRepository` bound to the request session."""
    return DocumentRepository(db)


def get_storage_service() -> StorageService:
    """Provide a :class:`StorageService`."""
    return StorageService()


def get_document_service(
    document_repository: Annotated[
        DocumentRepository, Depends(get_document_repository)
    ],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> DocumentService:
    """Provide a :class:`DocumentService` with its dependencies injected."""
    return DocumentService(document_repository, storage_service)


# --------------------------------------------------------------------------- #
# RAG providers
# --------------------------------------------------------------------------- #
def get_chunk_repository(db: DbSession) -> ChunkRepository:
    """Provide a :class:`ChunkRepository` bound to the request session."""
    return ChunkRepository(db)


def get_embedding_provider_dep() -> EmbeddingProvider:
    """Provide the configured embedding provider (cached singleton)."""
    return get_embedding_provider()


def get_processing_service() -> DocumentProcessingService:
    """Provide a :class:`DocumentProcessingService`."""
    return DocumentProcessingService()


def get_text_chunker() -> TextChunker:
    """Provide a :class:`TextChunker` using configured chunk size/overlap."""
    return TextChunker()


def get_ingestion_service(
    chunk_repository: Annotated[ChunkRepository, Depends(get_chunk_repository)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
    processing_service: Annotated[
        DocumentProcessingService, Depends(get_processing_service)
    ],
    chunker: Annotated[TextChunker, Depends(get_text_chunker)],
    embedding_provider: Annotated[
        EmbeddingProvider, Depends(get_embedding_provider_dep)
    ],
) -> IngestionService:
    """Provide an :class:`IngestionService` with its dependencies injected."""
    return IngestionService(
        chunk_repository,
        storage_service,
        processing_service,
        chunker,
        embedding_provider,
    )


def get_retrieval_service(
    chunk_repository: Annotated[ChunkRepository, Depends(get_chunk_repository)],
    embedding_provider: Annotated[
        EmbeddingProvider, Depends(get_embedding_provider_dep)
    ],
) -> RetrievalService:
    """Provide a :class:`RetrievalService` with its dependencies injected."""
    return RetrievalService(chunk_repository, embedding_provider)


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
    "get_document_repository",
    "get_storage_service",
    "get_document_service",
    "get_chunk_repository",
    "get_embedding_provider_dep",
    "get_processing_service",
    "get_text_chunker",
    "get_ingestion_service",
    "get_retrieval_service",
    "get_current_user",
    "require_role",
]
