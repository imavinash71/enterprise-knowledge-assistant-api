"""Document endpoints: upload, list, and delete."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import Response

from app.api.deps import CurrentUser, DbSession, get_document_service
from app.schemas.document import DocumentList, DocumentRead
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])

DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]


@router.post(
    "/upload",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
)
def upload_document(
    current_user: CurrentUser,
    db: DbSession,
    document_service: DocumentServiceDep,
    file: Annotated[UploadFile, File(description="The document to upload.")],
    title: Annotated[
        str | None, Form(description="Optional display title.")
    ] = None,
) -> DocumentRead:
    """Upload a PDF, DOCX, TXT, or PPTX file and store its metadata."""
    document = document_service.upload(file, owner=current_user, title=title)
    # Commit once the unit of work (file + metadata) has succeeded.
    db.commit()
    return DocumentRead.model_validate(document)


@router.get(
    "",
    response_model=DocumentList,
    summary="List the current user's documents",
)
def list_documents(
    current_user: CurrentUser,
    document_service: DocumentServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> DocumentList:
    """Return a paginated list of documents owned by the current user."""
    total, items = document_service.list_for_user(
        current_user, skip=skip, limit=limit
    )
    return DocumentList(
        total=total,
        items=[DocumentRead.model_validate(item) for item in items],
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a document",
)
def delete_document(
    document_id: int,
    current_user: CurrentUser,
    db: DbSession,
    document_service: DocumentServiceDep,
) -> Response:
    """Delete a document (metadata and stored file) owned by the user."""
    document_service.delete(document_id, current_user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
