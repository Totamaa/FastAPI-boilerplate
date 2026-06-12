"""Hard-delete soft-deleted records older than RETENTION_DAYS."""

import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete

from app.core.config.database import AsyncSessionLocal, UnitOfWork
from app.core.config.logs import get_logger
from app.modules.actors.model import ActorModel
from app.modules.directors.model import DirectorModel
from app.modules.genres.model import GenreModel
from app.modules.movie_cast.model import MovieCastModel
from app.modules.movies.model import MovieModel
from app.modules.reviews.model import ReviewModel
from app.modules.users.model import UserModel

logger = get_logger()

RETENTION_DAYS = 90

# Delete children before parents to avoid FK conflicts.
# DB-level CASCADE (ON DELETE CASCADE) covers any grandchildren.
_PURGE_ORDER = [
    ReviewModel,
    MovieCastModel,
    MovieModel,
    ActorModel,
    DirectorModel,
    GenreModel,
    UserModel,
]


async def purge_soft_deleted() -> None:
    cutoff = datetime.now(UTC) - timedelta(days=RETENTION_DAYS)
    logger.info("SCHEDULER:Purge", f"Hard-deleting soft-deleted records older than {cutoff.date()}")

    async with AsyncSessionLocal() as session, UnitOfWork(session):
        total = 0
        for model in _PURGE_ORDER:
            result = await session.execute(
                delete(model).where(
                    model.deleted_at.is_not(None),
                    model.deleted_at < cutoff,
                )
            )
            count = result.rowcount
            if count:
                logger.info("SCHEDULER:Purge", f"Purged {count} rows from {model.__tablename__}")
            total += count

    logger.info("SCHEDULER:Purge", f"Purge complete. Total rows removed: {total}")


def run() -> None:
    asyncio.run(purge_soft_deleted())
