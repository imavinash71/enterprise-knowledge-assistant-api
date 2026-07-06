"""Pydantic schemas package."""
from app.schemas.chat import (
    ChatBase,
    ChatCreate,
    ChatRead,
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
from app.schemas.document import DocumentBase, DocumentCreate, DocumentRead
from app.schemas.message import MessageBase, MessageCreate, MessageRead
from app.schemas.user import UserBase, UserCreate, UserRead, UserUpdate

__all__ = [
    # chat
    "ChatBase",
    "ChatCreate",
    "ChatRead",
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
    "DocumentRead",
    # message
    "MessageBase",
    "MessageCreate",
    "MessageRead",
    # user
    "UserBase",
    "UserCreate",
    "UserRead",
    "UserUpdate",
]
