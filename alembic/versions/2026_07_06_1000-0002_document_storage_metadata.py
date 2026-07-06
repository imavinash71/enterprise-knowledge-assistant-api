"""add file storage metadata to documents

Revision ID: 0002_document_storage_metadata
Revises: 0001_initial_schema
Create Date: 2026-07-06 10:00:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_document_storage_metadata"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # New columns are added as nullable first so the migration succeeds even if
    # rows already exist; ``file_path`` and ``file_size`` are then tightened to
    # NOT NULL. On an empty table this is effectively a no-op backfill.
    op.add_column(
        "documents", sa.Column("file_path", sa.String(length=1024), nullable=True)
    )
    op.add_column(
        "documents", sa.Column("file_size", sa.Integer(), nullable=True)
    )
    op.add_column(
        "documents",
        sa.Column("content_type", sa.String(length=255), nullable=True),
    )

    # Backfill sensible defaults for any pre-existing rows.
    op.execute(
        "UPDATE documents SET file_path = '' WHERE file_path IS NULL"
    )
    op.execute("UPDATE documents SET file_size = 0 WHERE file_size IS NULL")

    op.alter_column("documents", "file_path", nullable=False)
    op.alter_column("documents", "file_size", nullable=False)


def downgrade() -> None:
    op.drop_column("documents", "content_type")
    op.drop_column("documents", "file_size")
    op.drop_column("documents", "file_path")
