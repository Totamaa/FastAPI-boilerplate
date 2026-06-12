from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.logs import LoggerManager
from app.modules.actors.exceptions import ActorNotFoundException
from app.modules.actors.repository import ActorRepository
from app.modules.movie_cast.exceptions import (
    CastEntryAlreadyExistsException,
    CastEntryNotFoundException,
)
from app.modules.movie_cast.model import MovieCastModel
from app.modules.movie_cast.repository import MovieCastRepository
from app.modules.movie_cast.schemas import (
    CastEntryCreate,
    CastEntryDetailedResponse,
    CastEntryResponse,
    CastEntryUpdate,
)
from app.modules.movies.exceptions import MovieNotFoundException
from app.modules.movies.repository import MovieRepository


class MovieCastService:
    def __init__(
        self,
        logger: LoggerManager,
        session: AsyncSession,
        request_id: str,
        cast_repository: MovieCastRepository,
        movie_repository: MovieRepository,
        actor_repository: ActorRepository,
    ):
        self.tag = "SERVICE:MovieCast"
        self.logger = logger
        self.session = session
        self.request_id = request_id
        self.cast_repository = cast_repository
        self.movie_repository = movie_repository
        self.actor_repository = actor_repository

    async def get_by_movie(
        self, movie_id: UUID, limit: int = 20, offset: int = 0
    ) -> list[CastEntryDetailedResponse]:
        entries = await self.cast_repository.get_by_movie(
            movie_id=movie_id,
            db=self.session,
            limit=limit,
            offset=offset,
        )
        return [CastEntryDetailedResponse.from_model(e) for e in entries]

    async def add_to_cast(self, data: CastEntryCreate) -> CastEntryResponse:
        movie = await self.movie_repository.get_by_id(id=data.movie_id, db=self.session)
        if not movie:
            raise MovieNotFoundException(id=data.movie_id)

        actor = await self.actor_repository.get_by_id(id=data.actor_id, db=self.session)
        if not actor:
            raise ActorNotFoundException(id=data.actor_id)

        existing = await self.cast_repository.get_by_movie_and_actor(
            movie_id=data.movie_id,
            actor_id=data.actor_id,
            db=self.session,
        )
        if existing:
            raise CastEntryAlreadyExistsException(
                movie_id=data.movie_id,
                actor_id=data.actor_id,
            )

        self.logger.info(
            tag=self.tag,
            message=f"Adding actor_id={data.actor_id} to movie_id={data.movie_id}",
            extra=self.request_id,
        )
        entry = MovieCastModel(
            movie_id=data.movie_id,
            actor_id=data.actor_id,
            role_name=data.role_name,
            billing_order=data.billing_order,
            is_lead=data.is_lead,
        )
        await self.cast_repository.create(entry=entry, db=self.session)
        return CastEntryResponse.from_model(entry)

    async def update_cast_entry(self, id: UUID, data: CastEntryUpdate) -> CastEntryResponse:
        entry = await self.cast_repository.get_by_id(id=id, db=self.session)
        if not entry:
            raise CastEntryNotFoundException(id=id)

        update_data = data.model_dump(exclude_none=True)
        await self.cast_repository.update(entry=entry, data=update_data, db=self.session)

        self.logger.info(
            tag=self.tag,
            message=f"Updated cast entry id={id}",
            extra=self.request_id,
        )
        return CastEntryResponse.from_model(entry)

    async def remove_from_cast(self, id: UUID) -> None:
        entry = await self.cast_repository.get_by_id(id=id, db=self.session)
        if not entry:
            raise CastEntryNotFoundException(id=id)

        self.logger.info(
            tag=self.tag,
            message=f"Removing cast entry id={id}",
            extra=self.request_id,
        )
        await self.cast_repository.delete(entry=entry, db=self.session)
