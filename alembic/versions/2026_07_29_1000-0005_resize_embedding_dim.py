"""resize chunks.embedding vector dimension to match EMBEDDING_DIM

Revision ID: 0005_resize_embedding_dim
Revises: 0004_message_answer_metadata
Create Date: 2026-07-29 10:00:00.000000

Switching embedding providers/models can change the vector dimensionality
(e.g. OpenAI 1536 -> Ollama nomic-embed-text 768). pgvector fixes a column's
dimension at creation time, so the column must be re-typed to the new size.

Existing embeddings produced by a different model are incompatible and are
discarded here; documents must be re-ingested after this migration so their
chunks are re-embedded with the current model.
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from pgvector.sqlalchemy import Vector

from app.core.config import settings

# revision identifiers, used by Alembic.
revision: str = "0005_resize_embedding_dim"
down_revision: str | None = "0004_message_answer_metadata"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Previous fixed dimension (used for a best-effort downgrade).
_PREVIOUS_DIM = 1536


def _resize(target_dim: int) -> None:
    # The HNSW index is bound to the column's type, so drop it first.
    op.execute("DROP INDEX IF EXISTS ix_chunks_embedding_hnsw")
    # Old vectors have a different dimensionality and cannot be cast; clear them.
    # Chunks are re-created by re-ingesting documents.
    op.execute("DELETE FROM chunks")
    # Re-type the column to the new dimension.
    op.execute(
        f"ALTER TABLE chunks ALTER COLUMN embedding TYPE vector({target_dim}) "
        f"USING NULL"
    )
    # Recreate the cosine HNSW index to match the query-time distance function.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_chunks_embedding_hnsw "
        "ON chunks USING hnsw (embedding vector_cosine_ops)"
    )


def upgrade() -> None:
    _resize(settings.EMBEDDING_DIM)


def downgrade() -> None:
    _resize(_PREVIOUS_DIM)
