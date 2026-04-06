"""Initial schema: sessions, messages, traces

Revision ID: 0001
Revises:
Create Date: 2026-04-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "traces",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("request_id", sa.String(36), nullable=False, index=True),
        sa.Column("session_id", sa.String(36), nullable=True, index=True),
        sa.Column("user_id", sa.String(255), nullable=True),
        sa.Column("task_type", sa.String(50), nullable=False),
        sa.Column("selected_agent", sa.String(100), nullable=False),
        sa.Column("selected_provider", sa.String(100), nullable=False),
        sa.Column("selected_model", sa.String(200), nullable=False),
        sa.Column("fallback_used", sa.Boolean, nullable=False, default=False),
        sa.Column("latency_ms", sa.Float, nullable=False),
        sa.Column("prompt_tokens", sa.Integer, nullable=True),
        sa.Column("completion_tokens", sa.Integer, nullable=True),
        sa.Column("success", sa.Boolean, nullable=False, default=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("tool_calls_summary", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("traces")
    op.drop_table("messages")
    op.drop_table("sessions")
