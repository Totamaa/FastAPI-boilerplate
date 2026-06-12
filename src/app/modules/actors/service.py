from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.logs import LoggerManager
from app.modules.actors.exceptions import ActorNotFoundException
from app.modules.actors.repository import ActorRepository
from app.modules.actors.schemas import ActorCreate, ActorResponse, ActorUpdate

TAG = "actors"


class ActorService:
    def __init__(
        self,
        logger: LoggerManager,
        session: AsyncSession,
        request_id: str,
        actor_repository: ActorRepository,
    ):
        self.logger = logger
        self.session = session
        self.request_id = request_id
        self.actor_repository = actor_repository

    async def get_all(self, limit: int = 20, offset: int = 0) -> list[ActorResponse]:
        actors = await self.actor_repository.get_all(self.session, limit=limit, offset=offset)
        return [ActorResponse.from_model(a) for a in actors]

    async def get_by_id(self, id: UUID, include_movies: bool = False) -> ActorResponse:
        """Fetch an actor. Pass include_movies=True to embed filmography (cas 3 — single DB call)."""
        if include_movies:
            actor = await self.actor_repository.get_with_cast(id, self.session)
        else:
            actor = await self.actor_repository.get_by_id(id, self.session)
        if actor is None:
            raise ActorNotFoundException(id)
        return ActorResponse.from_model(actor, include_movies=include_movies)

    async def create(self, data: ActorCreate) -> ActorResponse:
        actor = data.to_model()
        actor = await self.actor_repository.create(actor, self.session)
        self.logger.info(TAG, "Actor created", extra=f"id={actor.id}")
        return ActorResponse.from_model(actor)

    async def update(self, id: UUID, data: ActorUpdate) -> ActorResponse:
        actor = await self.actor_repository.get_by_id(id, self.session)
        if actor is None:
            raise ActorNotFoundException(id)
        actor = await self.actor_repository.update(
            actor, data.model_dump(exclude_unset=True), self.session
        )
        return ActorResponse.from_model(actor)

    async def delete(self, id: UUID) -> None:
        actor = await self.actor_repository.get_by_id(id, self.session)
        if actor is None:
            raise ActorNotFoundException(id)
        await self.actor_repository.delete(actor, self.session)
        self.logger.info(TAG, "Actor deleted", extra=f"id={id}")
