from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.db import get_session
from app.core.api.dependencies.request_id import get_request_id
from app.core.config.logs import LoggerManager, get_logger
from app.modules.actors.repository import ActorRepository
from app.modules.actors.service import ActorService


def get_actor_repository() -> ActorRepository:
    return ActorRepository()


def get_actor_service(
    logger: LoggerManager = Depends(get_logger),
    session: AsyncSession = Depends(get_session),
    request_id: str = Depends(get_request_id),
    repo: ActorRepository = Depends(get_actor_repository),
) -> ActorService:
    return ActorService(
        logger=logger,
        session=session,
        request_id=request_id,
        actor_repository=repo,
    )
