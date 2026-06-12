from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.db import get_session
from app.core.api.dependencies.request_id import get_request_id
from app.core.config.logs import get_logger
from app.modules.movies.dependencies import get_movie_repository
from app.modules.movies.repository import MovieRepository
from app.modules.reviews.repository import ReviewRepository
from app.modules.reviews.service import ReviewService


def get_review_repository() -> ReviewRepository:
    return ReviewRepository()


def get_review_service(
    logger=Depends(get_logger),
    session: AsyncSession = Depends(get_session),
    request_id: str = Depends(get_request_id),
    review_repo: ReviewRepository = Depends(get_review_repository),
    movie_repo: MovieRepository = Depends(get_movie_repository),
) -> ReviewService:
    return ReviewService(
        logger=logger,
        session=session,
        request_id=request_id,
        review_repository=review_repo,
        movie_repository=movie_repo,
    )
