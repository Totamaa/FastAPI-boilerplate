from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.db import get_session
from app.core.api.dependencies.request_id import get_request_id
from app.core.config.logs import get_logger
from app.modules.genres.repository import GenreRepository
from app.modules.movies.repository import MovieRepository
from app.modules.movies.service import MovieService


def get_movie_repository() -> MovieRepository:
    return MovieRepository()


def _get_genre_repository() -> GenreRepository:
    return GenreRepository()


def get_movie_service(
    logger=Depends(get_logger),
    session: AsyncSession = Depends(get_session),
    request_id: str = Depends(get_request_id),
    movie_repo: MovieRepository = Depends(get_movie_repository),
    genre_repo: GenreRepository = Depends(_get_genre_repository),
) -> MovieService:
    return MovieService(
        logger=logger,
        session=session,
        request_id=request_id,
        movie_repository=movie_repo,
        genre_repository=genre_repo,
    )
