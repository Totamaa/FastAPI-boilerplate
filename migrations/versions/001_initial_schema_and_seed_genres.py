"""initial schema and seed genres

Revision ID: 001
Revises: 
Create Date: 2026-06-11
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── directors ─────────────────────────────────────────────────────────────
    op.create_table(
        "directors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("nationality", sa.String(100), nullable=True),
        sa.Column("biography", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── genres ────────────────────────────────────────────────────────────────
    op.create_table(
        "genres",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_genres_slug", "genres", ["slug"], unique=True)

    # ── actors ────────────────────────────────────────────────────────────────
    op.create_table(
        "actors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("nationality", sa.String(100), nullable=True),
        sa.Column("biography", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(256), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── movies ────────────────────────────────────────────────────────────────
    op.create_table(
        "movies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("release_year", sa.Integer(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("language", sa.String(5), nullable=True),
        sa.Column(
            "status",
            sa.Enum("released", "upcoming", "cancelled", name="movie_status", create_constraint=True, native_enum=False),
            nullable=False,
            server_default="released",
        ),
        sa.Column("avg_rating", sa.Float(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "director_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("directors.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_movies_director_id", "movies", ["director_id"])
    op.create_index("ix_movies_release_year", "movies", ["release_year"])
    op.create_index("ix_movies_status", "movies", ["status"])

    # ── movie_genres (N-N simple junction) ────────────────────────────────────
    op.create_table(
        "movie_genres",
        sa.Column(
            "movie_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("movies.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "genre_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("genres.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # ── movie_details (1-1) ───────────────────────────────────────────────────
    op.create_table(
        "movie_details",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "movie_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("movies.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("synopsis", sa.Text(), nullable=True),
        sa.Column("budget_usd", sa.BigInteger(), nullable=True),
        sa.Column("box_office_usd", sa.BigInteger(), nullable=True),
        sa.Column("awards_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_movie_details_movie_id", "movie_details", ["movie_id"])

    # ── movie_cast (N-N with data) ────────────────────────────────────────────
    op.create_table(
        "movie_cast",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "movie_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("movies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "actor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("actors.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role_name", sa.String(255), nullable=False),
        sa.Column("billing_order", sa.Integer(), nullable=False),
        sa.Column("is_lead", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("movie_id", "actor_id", name="uq_movie_cast_movie_actor"),
    )
    op.create_index("ix_movie_cast_movie_id", "movie_cast", ["movie_id"])
    op.create_index("ix_movie_cast_actor_id", "movie_cast", ["actor_id"])

    # ── reviews ───────────────────────────────────────────────────────────────
    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "movie_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("movies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("contains_spoilers", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("rating >= 1 AND rating <= 10", name="ck_reviews_rating_range"),
        sa.UniqueConstraint("user_id", "movie_id", name="uq_reviews_user_movie"),
    )
    op.create_index("ix_reviews_movie_id", "reviews", ["movie_id"])
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"])

    # ── seed genres ───────────────────────────────────────────────────────────
    op.execute("""
        INSERT INTO genres (id, name, slug, created_at, updated_at) VALUES
        (gen_random_uuid(), 'Action',      'action',      now(), now()),
        (gen_random_uuid(), 'Adventure',   'adventure',   now(), now()),
        (gen_random_uuid(), 'Animation',   'animation',   now(), now()),
        (gen_random_uuid(), 'Comedy',      'comedy',      now(), now()),
        (gen_random_uuid(), 'Crime',       'crime',       now(), now()),
        (gen_random_uuid(), 'Documentary', 'documentary', now(), now()),
        (gen_random_uuid(), 'Drama',       'drama',       now(), now()),
        (gen_random_uuid(), 'Fantasy',     'fantasy',     now(), now()),
        (gen_random_uuid(), 'Horror',      'horror',      now(), now()),
        (gen_random_uuid(), 'Romance',     'romance',     now(), now()),
        (gen_random_uuid(), 'Science Fiction', 'sci-fi',  now(), now()),
        (gen_random_uuid(), 'Thriller',    'thriller',    now(), now())
    """)


def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_table("movie_cast")
    op.drop_table("movie_details")
    op.drop_table("movie_genres")
    op.drop_table("movies")
    op.drop_table("users")
    op.drop_table("actors")
    op.drop_table("genres")
    op.drop_table("directors")
