from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.db import get_session
from app.core.api.dependencies.request_id import get_request_id
from app.core.config.logs import LoggerManager, get_logger
from app.modules.genres.repository import GenreRepository
from app.modules.genres.service import GenreService


def get_genre_repository() -> GenreRepository:
    return GenreRepository()


def get_genre_service(
    logger: LoggerManager = Depends(get_logger),
    session: AsyncSession = Depends(get_session),
    request_id: str = Depends(get_request_id),
    repo: GenreRepository = Depends(get_genre_repository),
) -> GenreService:
    return GenreService(
        logger=logger,
        session=session,
        request_id=request_id,
        genre_repository=repo,
    )
