"""add answer metadata (sources, confidence) to messages

Revision ID: 0004_message_answer_metadata
Revises: 0003_chunks_embedding_index
Create Date: 2026-07-07 09:00:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0004_message_answer_metadata"
down_revision: str | None = "0003_chunks_embedding_index"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Nullable assistant-answer metadata: retrieved sources (JSONB) and the
    # agent's confidence score. NULL for user/system messages.
    op.add_column(
        "messages",
        sa.Column("sources", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "messages", sa.Column("confidence", sa.Float(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("messages", "confidence")
    op.drop_column("messages", "sources")
