from sqlalchemy import func, select, update

from app.core.config.database import AsyncSessionLocal, UnitOfWork
from app.core.config.logs import get_logger
from app.modules.movies.model import MovieModel
from app.modules.reviews.model import ReviewModel

logger = get_logger()


async def refresh_all_movie_stats() -> None:
    """Recomputes avg_rating and review_count for every movie from the reviews table."""
    logger.info("SCHEDULER:MovieStats", "Starting daily movie stats refresh")

    async with AsyncSessionLocal() as session, UnitOfWork(session):
        result = await session.execute(select(MovieModel.id))
        movie_ids = [row[0] for row in result.fetchall()]

        updated = 0
        for movie_id in movie_ids:
            stats_result = await session.execute(
                select(func.avg(ReviewModel.rating), func.count(ReviewModel.id)).where(
                    ReviewModel.movie_id == movie_id
                )
            )
            avg, count = stats_result.one()
            await session.execute(
                update(MovieModel)
                .where(MovieModel.id == movie_id)
                .values(
                    avg_rating=float(avg) if avg is not None else None,
                    review_count=count or 0,
                )
            )
            updated += 1

        logger.info("SCHEDULER:MovieStats", f"Refreshed stats for {updated} movies")


def run() -> None:
    """Sync entry point for APScheduler — wraps the async job in a new event loop."""
    import asyncio

    asyncio.run(refresh_all_movie_stats())
