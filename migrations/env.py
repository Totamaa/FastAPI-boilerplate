import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models for autogenerate support
from app.modules.actors.model import ActorModel  # noqa: F401
from app.modules.associations.movie_genres import movie_genres  # noqa: F401 — registers the table
from app.modules.audit_logs.model import AuditLogModel  # noqa: F401
from app.modules.base.model import BaseModel
from app.modules.directors.model import DirectorModel  # noqa: F401
from app.modules.genres.model import GenreModel  # noqa: F401
from app.modules.movie_cast.model import MovieCastModel  # noqa: F401
from app.modules.movie_details.model import MovieDetailModel  # noqa: F401
from app.modules.movies.model import MovieModel  # noqa: F401
from app.modules.reviews.model import ReviewModel  # noqa: F401
from app.modules.tokens.model import RefreshTokenFamilyModel, RefreshTokenModel  # noqa: F401
from app.modules.users.model import UserModel  # noqa: F401
from app.modules.feature_flags.model import FeatureFlagModel  # noqa: F401

target_metadata = BaseModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
if not config.get_main_option("sqlalchemy.url", None):
    from app.core.config.settings import get_settings
    settings = get_settings()
    database_url = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    config.set_main_option("sqlalchemy.url", database_url)



def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
