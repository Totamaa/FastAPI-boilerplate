from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.db import get_session
from app.core.api.dependencies.request_id import get_request_id
from app.core.config.logs import get_logger
from app.modules.actors.repository import ActorRepository
from app.modules.movie_cast.repository import MovieCastRepository
from app.modules.movie_cast.service import MovieCastService
from app.modules.movies.dependencies import get_movie_repository
from app.modules.movies.repository import MovieRepository


def get_movie_cast_repository() -> MovieCastRepository:
    return MovieCastRepository()


def _get_actor_repository() -> ActorRepository:
    return ActorRepository()


def get_movie_cast_service(
    logger=Depends(get_logger),
    session: AsyncSession = Depends(get_session),
    request_id: str = Depends(get_request_id),
    cast_repo: MovieCastRepository = Depends(get_movie_cast_repository),
    movie_repo: MovieRepository = Depends(get_movie_repository),
    actor_repo: ActorRepository = Depends(_get_actor_repository),
) -> MovieCastService:
    return MovieCastService(
        logger=logger,
        session=session,
        request_id=request_id,
        cast_repository=cast_repo,
        movie_repository=movie_repo,
        actor_repository=actor_repo,
    )
