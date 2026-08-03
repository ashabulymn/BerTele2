from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260803_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("api_id", sa.Integer(), nullable=False),
        sa.Column("api_hash", sa.String(length=255), nullable=False),
        sa.Column("session_string", sa.Text(), nullable=True),
        sa.Column("phone_number", sa.String(length=64), nullable=True),
        sa.Column("bot_token", sa.String(length=255), nullable=True),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("last_connected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("sessions")
