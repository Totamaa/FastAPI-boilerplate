from uuid import UUID

from sqlalchemy import func, select, update

from app.core.config.database import AsyncSessionLocal, UnitOfWork
from app.core.config.logs import get_logger
from app.modules.movies.model import MovieModel
from app.modules.reviews.model import ReviewModel

logger = get_logger()


async def update_movie_stats_after_review(movie_id: UUID) -> None:
    """
    Recomputes avg_rating and review_count for a single movie.
    Called as a FastAPI BackgroundTask after a review is created or deleted.
    """
    logger.info("BACKGROUND:MovieStats", f"Updating stats for movie_id={movie_id}")

    async with AsyncSessionLocal() as session, UnitOfWork(session):
        result = await session.execute(
            select(func.avg(ReviewModel.rating), func.count(ReviewModel.id)).where(
                ReviewModel.movie_id == movie_id
            )
        )
        avg, count = result.one()

        await session.execute(
            update(MovieModel)
            .where(MovieModel.id == movie_id)
            .values(
                avg_rating=float(avg) if avg is not None else None,
                review_count=count or 0,
            )
        )

    logger.info("BACKGROUND:MovieStats", f"Stats updated for movie_id={movie_id}")
