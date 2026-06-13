"""add feature_flags table with seed data

Revision ID: 005
Revises: 004
Create Date: 2026-06-13
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, UUID

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feature_flags",
        sa.Column("key", sa.Text, primary_key=True, nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("rollout_percentage", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "allowed_user_ids",
            ARRAY(UUID(as_uuid=True)),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.execute("""
        INSERT INTO feature_flags (key, enabled, rollout_percentage, description, updated_at)
        VALUES
        ('movies:listing_enabled', true,  100, 'Kill switch for movie listing endpoint', now()),
        ('actors:show_biography',  true,   25, '25%% progressive rollout',               now()),
        ('reviews:premium_features', false, 0, 'Beta access for premium reviewers',      now())
    """)


def downgrade() -> None:
    op.drop_table("feature_flags")
