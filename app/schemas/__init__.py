"""Pydantic schemas package."""
from app.schemas.agent import AskRequest, AskResponse, CitationOut
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPayload,
    TokenResponse,
)
from app.schemas.chat import (
    ChatBase,
    ChatCreate,
    ChatHistory,
    ChatRead,
    ChatRequest,
    ChatResponse,
    ChatUpdate,
    ChatWithMessages,
)
from app.schemas.chunk import (
    ChunkBase,
    ChunkCreate,
    ChunkRead,
    ChunkSearchResult,
)
from app.schemas.common import ErrorDetail, ErrorResponse, Message, ORMModel
from app.schemas.document import (
    DocumentBase,
    DocumentCreate,
    DocumentList,
    DocumentRead,
)
from app.schemas.message import MessageBase, MessageCreate, MessageRead
from app.schemas.rag import (
    IngestResponse,
    SearchRequest,
    SearchResponse,
)
from app.schemas.user import UserBase, UserCreate, UserRead, UserUpdate

__all__ = [
    # agent
    "AskRequest",
    "AskResponse",
    "CitationOut",
    # auth
    "AuthResponse",
    "LoginRequest",
    "RefreshRequest",
    "RegisterRequest",
    "TokenPayload",
    "TokenResponse",
    # chat
    "ChatBase",
    "ChatCreate",
    "ChatHistory",
    "ChatRead",
    "ChatRequest",
    "ChatResponse",
    "ChatUpdate",
    "ChatWithMessages",
    # chunk
    "ChunkBase",
    "ChunkCreate",
    "ChunkRead",
    "ChunkSearchResult",
    # common
    "ErrorDetail",
    "ErrorResponse",
    "Message",
    "ORMModel",
    # document
    "DocumentBase",
    "DocumentCreate",
    "DocumentList",
    "DocumentRead",
    # message
    "MessageBase",
    "MessageCreate",
    "MessageRead",
    # rag
    "IngestResponse",
    "SearchRequest",
    "SearchResponse",
    # user
    "UserBase",
    "UserCreate",
    "UserRead",
    "UserUpdate",
]
