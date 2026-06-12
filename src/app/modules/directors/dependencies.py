from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.db import get_session
from app.core.api.dependencies.request_id import get_request_id
from app.core.config.logs import LoggerManager, get_logger
from app.modules.directors.repository import DirectorRepository
from app.modules.directors.service import DirectorService
from app.modules.movies.repository import MovieRepository


def get_director_repository() -> DirectorRepository:
    return DirectorRepository()


def _get_movie_repository() -> MovieRepository:
    return MovieRepository()


def get_director_service(
    logger: LoggerManager = Depends(get_logger),
    session: AsyncSession = Depends(get_session),
    request_id: str = Depends(get_request_id),
    repo: DirectorRepository = Depends(get_director_repository),
    movie_repo: MovieRepository = Depends(_get_movie_repository),
) -> DirectorService:
    return DirectorService(
        logger=logger,
        session=session,
        request_id=request_id,
        director_repository=repo,
        movie_repository=movie_repo,
    )
