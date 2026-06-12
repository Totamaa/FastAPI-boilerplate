from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.db import get_session
from app.core.api.dependencies.request_id import get_request_id
from app.core.config.logs import get_logger
from app.modules.movie_details.repository import MovieDetailRepository
from app.modules.movie_details.service import MovieDetailService
from app.modules.movies.dependencies import get_movie_repository
from app.modules.movies.repository import MovieRepository


def get_movie_detail_repository() -> MovieDetailRepository:
    return MovieDetailRepository()


def get_movie_detail_service(
    logger=Depends(get_logger),
    session: AsyncSession = Depends(get_session),
    request_id: str = Depends(get_request_id),
    detail_repo: MovieDetailRepository = Depends(get_movie_detail_repository),
    movie_repo: MovieRepository = Depends(get_movie_repository),
) -> MovieDetailService:
    return MovieDetailService(
        logger=logger,
        session=session,
        request_id=request_id,
        detail_repository=detail_repo,
        movie_repository=movie_repo,
    )
