from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, func, select

from app.core.config.database import AsyncSessionLocal
from app.core.config.logs import get_logger
from app.modules.movies.model import MovieModel
from app.modules.reviews.model import ReviewModel

logger = get_logger()


async def log_trending_movies(top_n: int = 10) -> None:
    """Logs the top N movies by review count in the last 7 days."""
    logger.info("SCHEDULER:Trending", "Computing weekly trending movies")

    since = datetime.now(UTC) - timedelta(days=7)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MovieModel.id, MovieModel.title, func.count(ReviewModel.id).label("new_reviews"))
            .join(ReviewModel, ReviewModel.movie_id == MovieModel.id)
            .where(ReviewModel.created_at >= since)
            .group_by(MovieModel.id, MovieModel.title)
            .order_by(desc("new_reviews"))
            .limit(top_n)
        )
        rows = result.fetchall()

        if not rows:
            logger.info("SCHEDULER:Trending", "No reviews in the last 7 days")
            return

        for i, (_movie_id, title, count) in enumerate(rows, 1):
            logger.info("SCHEDULER:Trending", f"#{i} {title!r} — {count} new review(s)")


def run() -> None:
    """Sync entry point for APScheduler — wraps the async job in a new event loop."""
    import asyncio

    asyncio.run(log_trending_movies())
