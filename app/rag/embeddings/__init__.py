"""Embedding providers.

Defines a provider-agnostic interface for turning text into embedding vectors,
with concrete strategies for OpenAI, Gemini, and a deterministic local "fake"
provider. Provider SDKs are imported lazily so the app only requires the
package for the provider actually in use.
"""
from app.rag.embeddings.base import EmbeddingProvider
from app.rag.embeddings.factory import get_embedding_provider

__all__ = ["EmbeddingProvider", "get_embedding_provider"]
