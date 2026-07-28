"""Chat service: run the agent, persist the conversation, and read history.

Flow for a single turn:
    receive question -> run LangGraph agent -> persist user + assistant
    messages (assistant message stores retrieved sources + confidence) ->
    return answer, sources and confidence.

Conversations live in PostgreSQL as ``Chat`` (thread) + ordered ``Message``
rows. All reads/writes are scoped to the requesting user for isolation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.logging import get_logger
from app.models.chat import Chat
from app.models.enums import MessageRole, UserRole
from app.models.message import Message
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.services.agent_service import AgentAnswer, AgentService

from app.agents.state import RetrievedSource

logger = get_logger(__name__)

# Title new chats from the opening question, trimmed to a sensible length.
_TITLE_MAX_LEN = 80


@dataclass
class ChatTurn:
    """Result of answering one chat message."""

    chat_id: int
    question: str
    answer: str
    intent: str
    confidence: float
    verified: bool
    sources: list[RetrievedSource]


class ChatService:
    """Orchestrates agent answers and conversation persistence."""

    def __init__(
        self,
        chat_repository: ChatRepository,
        message_repository: MessageRepository,
        agent_service: AgentService,
    ) -> None:
        self._chats = chat_repository
        self._messages = message_repository
        self._agent = agent_service

    def ask(
        self,
        question: str,
        user: User,
        *,
        chat_id: int | None = None,
        document_id: int | None = None,
        top_k: int | None = None,
    ) -> ChatTurn:
        """Answer ``question`` and persist the exchange.

        Args:
            question: The user's message.
            user: The authenticated user (owns the conversation and documents).
            chat_id: Continue this conversation; a new chat is created if None.
            document_id: Restrict retrieval to a single document.
            top_k: Number of chunks to retrieve.

        Raises:
            NotFoundError / ForbiddenError: If ``chat_id`` is given but does not
                exist or is not owned by ``user``.
        """
        result: AgentAnswer = self._agent.answer(
            question,
            owner_id=user.id,
            document_id=document_id,
            top_k=top_k,
        )

        chat = (
            self._get_owned(chat_id, user)
            if chat_id is not None
            else self._chats.add(
                Chat(user_id=user.id, title=self._make_title(question))
            )
        )

        # Persist the turn: user question followed by the assistant answer.
        self._messages.add(
            Message(
                chat_id=chat.id,
                role=MessageRole.USER.value,
                message=question,
            )
        )
        self._messages.add(
            Message(
                chat_id=chat.id,
                role=MessageRole.ASSISTANT.value,
                message=result.answer,
                # Cast the TypedDicts to plain dicts for JSONB storage.
                sources=[dict(source) for source in result.sources],
                confidence=result.confidence,
            )
        )
        logger.info(
            "Persisted chat turn: chat_id=%s intent=%s confidence=%.4f",
            chat.id,
            result.intent,
            result.confidence,
        )

        return ChatTurn(
            chat_id=chat.id,
            question=question,
            answer=result.answer,
            intent=result.intent,
            confidence=result.confidence,
            verified=result.verified,
            sources=result.sources,
        )

    def list_history(
        self, user: User, *, skip: int = 0, limit: int = 50
    ) -> tuple[Sequence[Chat], int]:
        """Return the user's conversations (with messages) and the total count."""
        chats = self._chats.list_by_user(user.id, skip=skip, limit=limit)
        total = self._chats.count_by_user(user.id)
        return chats, total

    def delete_chat(self, chat_id: int, user: User) -> None:
        """Delete a conversation the user owns (messages cascade)."""
        chat = self._get_owned(chat_id, user)
        self._chats.delete(chat)
        logger.info("Deleted chat_id=%s for user_id=%s", chat_id, user.id)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _get_owned(self, chat_id: int, user: User) -> Chat:
        """Fetch a chat, enforcing ownership (admins may access any chat)."""
        chat = self._chats.get_with_messages(chat_id)
        if chat is None:
            raise NotFoundError("Chat not found.")
        if chat.user_id != user.id and user.role != UserRole.ADMIN.value:
            raise ForbiddenError("You do not have access to this conversation.")
        return chat

    @staticmethod
    def _make_title(question: str) -> str:
        """Build a concise chat title from the opening question."""
        title = " ".join(question.split()).strip()
        if len(title) > _TITLE_MAX_LEN:
            title = title[: _TITLE_MAX_LEN - 1].rstrip() + "\u2026"
        return title or "New conversation"
