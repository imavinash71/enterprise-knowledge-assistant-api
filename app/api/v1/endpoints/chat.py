"""Chat endpoints: converse with the knowledge assistant and manage history."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import CurrentUser, DbSession, get_chat_service
from app.schemas.agent import CitationOut
from app.schemas.chat import (
    ChatHistory,
    ChatRequest,
    ChatResponse,
    ChatWithMessages,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])

ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ask a question and persist the conversation",
)
def create_chat_message(
    payload: ChatRequest,
    current_user: CurrentUser,
    db: DbSession,
    chat_service: ChatServiceDep,
) -> ChatResponse:
    """Run the agent for ``payload.question`` and store the exchange.

    Starts a new conversation unless ``chat_id`` references an existing one the
    user owns. Returns the answer, its retrieved sources and a confidence score.
    """
    turn = chat_service.ask(
        payload.question,
        current_user,
        chat_id=payload.chat_id,
        document_id=payload.document_id,
        top_k=payload.top_k,
    )
    # Commit once the full turn (chat + both messages) has been staged.
    db.commit()
    return ChatResponse(
        chat_id=turn.chat_id,
        question=turn.question,
        answer=turn.answer,
        intent=turn.intent,
        confidence=turn.confidence,
        verified=turn.verified,
        sources=[CitationOut(**source) for source in turn.sources],
    )


@router.get(
    "/history",
    response_model=ChatHistory,
    summary="List the current user's conversations",
)
def get_chat_history(
    current_user: CurrentUser,
    chat_service: ChatServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ChatHistory:
    """Return the user's conversations (with messages), most recent first."""
    chats, total = chat_service.list_history(current_user, skip=skip, limit=limit)
    return ChatHistory(
        total=total,
        items=[ChatWithMessages.model_validate(chat) for chat in chats],
    )


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a conversation",
)
def delete_chat(
    chat_id: int,
    current_user: CurrentUser,
    db: DbSession,
    chat_service: ChatServiceDep,
) -> Response:
    """Delete a conversation the user owns; its messages cascade."""
    chat_service.delete_chat(chat_id, current_user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
