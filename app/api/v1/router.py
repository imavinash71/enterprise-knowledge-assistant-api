"""Aggregate router for API version 1."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import agent, auth, chat, documents, health, rag

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(rag.router)
api_router.include_router(agent.router)
api_router.include_router(chat.router)
