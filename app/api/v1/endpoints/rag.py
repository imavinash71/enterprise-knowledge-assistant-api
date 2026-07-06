"""RAG endpoints: document ingestion and similarity search."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import (
    CurrentUser,
    DbSession,
    get_document_service,
    get_ingestion_service,
    get_retrieval_service,
)
from app.schemas.chunk import ChunkSearchResult
from app.schemas.rag import IngestResponse, SearchRequest, SearchResponse
from app.services.document_service import DocumentService
from app.services.ingestion_service import IngestionService
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/rag", tags=["rag"])

IngestionServiceDep = Annotated[IngestionService, Depends(get_ingestion_service)]
RetrievalServiceDep = Annotated[RetrievalService, Depends(get_retrieval_service)]
DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]


@router.post(
    "/documents/{document_id}/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a document into the vector store",
)
def ingest_document(
    document_id: int,
    current_user: CurrentUser,
    db: DbSession,
    ingestion_service: IngestionServiceDep,
    document_service: DocumentServiceDep,
) -> IngestResponse:
    """Extract, chunk, embed and store a document the user owns."""
    # Ownership/existence is enforced here before any heavy processing.
    document = document_service.get_owned(document_id, current_user)
    chunks_created = ingestion_service.ingest(document)
    db.commit()
    return IngestResponse(
        document_id=document.id, chunks_created=chunks_created
    )


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Similarity search over ingested documents",
)
def search(
    payload: SearchRequest,
    current_user: CurrentUser,
    retrieval_service: RetrievalServiceDep,
) -> SearchResponse:
    """Return the top-K chunks most relevant to the query.

    Results are scoped to documents owned by the current user.
    """
    scored = retrieval_service.search(
        payload.query,
        owner_id=current_user.id,
        document_id=payload.document_id,
        top_k=payload.top_k,
    )
    results = [
        ChunkSearchResult(
            id=item.chunk.id,
            document_id=item.chunk.document_id,
            content=item.chunk.content,
            score=item.score,
        )
        for item in scored
    ]
    return SearchResponse(query=payload.query, results=results)
