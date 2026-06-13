"""add audit logs table

Revision ID: 004
Revises: 003
Create Date: 2026-06-13
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("actor_id", UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.Text, nullable=False),
        sa.Column("target_type", sa.Text, nullable=True),
        sa.Column("target_id", UUID(as_uuid=True), nullable=True),
        sa.Column("diff", JSONB, nullable=True),
        sa.Column("ip", sa.Text, nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_logs_target", "audit_logs", ["target_type", "target_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    # Enforce immutability at DB level.
    # The app role should also have only INSERT + SELECT (no UPDATE/DELETE).
    op.execute(
        "CREATE RULE no_update_audit AS ON UPDATE TO audit_logs DO INSTEAD NOTHING;"
    )
    op.execute(
        "CREATE RULE no_delete_audit AS ON DELETE TO audit_logs DO INSTEAD NOTHING;"
    )


def downgrade() -> None:
    op.execute("DROP RULE IF EXISTS no_delete_audit ON audit_logs;")
    op.execute("DROP RULE IF EXISTS no_update_audit ON audit_logs;")

    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_target", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor_id", table_name="audit_logs")

    op.drop_table("audit_logs")
