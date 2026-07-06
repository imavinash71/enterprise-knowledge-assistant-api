"""Agent endpoint: ask the LangGraph knowledge assistant a question."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, get_agent_service
from app.schemas.agent import AskRequest, AskResponse, CitationOut
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agent", tags=["agent"])

AgentServiceDep = Annotated[AgentService, Depends(get_agent_service)]


@router.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask the knowledge assistant a question",
)
def ask(
    payload: AskRequest,
    current_user: CurrentUser,
    agent_service: AgentServiceDep,
) -> AskResponse:
    """Run the agent workflow and return a citation-verified answer.

    Retrieval is scoped to documents owned by the authenticated user so a user
    can never surface another user's content.
    """
    result = agent_service.answer(
        payload.question,
        owner_id=current_user.id,
        document_id=payload.document_id,
        top_k=payload.top_k,
    )
    return AskResponse(
        question=result.question,
        intent=result.intent,
        answer=result.answer,
        verified=result.verified,
        verification_notes=result.verification_notes,
        citations=[CitationOut(**source) for source in result.citations],
    )
