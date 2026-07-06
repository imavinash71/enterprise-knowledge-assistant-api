"""add hnsw index on chunks.embedding for similarity search

Revision ID: 0003_chunks_embedding_index
Revises: 0002_document_storage_metadata
Create Date: 2026-07-06 11:00:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_chunks_embedding_index"
down_revision: str | None = "0002_document_storage_metadata"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # HNSW index with cosine distance to accelerate similarity search. The
    # operator class (``vector_cosine_ops``) must match the distance function
    # used at query time (``cosine_distance``).
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_chunks_embedding_hnsw "
        "ON chunks USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_chunks_embedding_hnsw")
