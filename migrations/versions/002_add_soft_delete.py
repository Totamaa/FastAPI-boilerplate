"""add soft delete

Revision ID: 002
Revises: 001
Create Date: 2026-06-12
"""

import sqlalchemy as sa
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

_TABLES = [
    "actors",
    "directors",
    "genres",
    "movies",
    "users",
    "reviews",
    "movie_cast",
    "movie_details",
]


def upgrade() -> None:
    for table in _TABLES:
        op.add_column(table, sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    # Replace the redundant unique constraint + index on users.email with a
    # partial unique index so that soft-deleted emails can be reused.
    op.drop_constraint("users_email_key", "users", type_="unique")
    op.drop_index("ix_users_email", table_name="users")
    op.create_index(
        "uq_users_email_active",
        "users",
        ["email"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # Partial indexes on frequently filtered FK columns to avoid full-table scans.
    op.create_index(
        "ix_reviews_movie_id_active",
        "reviews",
        ["movie_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_movie_cast_movie_id_active",
        "movie_cast",
        ["movie_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_movie_cast_movie_id_active", table_name="movie_cast")
    op.drop_index("ix_reviews_movie_id_active", table_name="reviews")

    op.drop_index("uq_users_email_active", table_name="users")
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_unique_constraint("users_email_key", "users", ["email"])

    for table in reversed(_TABLES):
        op.drop_column(table, "deleted_at")
