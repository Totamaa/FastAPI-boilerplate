from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.logs import LoggerManager
from app.modules.directors.exceptions import DirectorNotFoundException
from app.modules.directors.repository import DirectorRepository
from app.modules.directors.schemas import DirectorCreate, DirectorResponse, DirectorUpdate

TAG = "directors"


class DirectorService:
    def __init__(
        self,
        logger: LoggerManager,
        session: AsyncSession,
        request_id: str,
        director_repository: DirectorRepository,
    ):
        self.logger = logger
        self.session = session
        self.request_id = request_id
        self.director_repository = director_repository

    # ── standard CRUD ────────────────────────────────────────────────────────

    async def get_all(self, limit: int = 20, offset: int = 0) -> list[DirectorResponse]:
        directors = await self.director_repository.get_all(self.session, limit=limit, offset=offset)
        return [DirectorResponse.from_model(d) for d in directors]

    async def get_by_id(self, id: UUID) -> DirectorResponse:
        director = await self.director_repository.get_by_id(id, self.session)
        if director is None:
            raise DirectorNotFoundException(id)
        return DirectorResponse.from_model(director)

    async def create(self, data: DirectorCreate) -> DirectorResponse:
        director = data.to_model()
        director = await self.director_repository.create(director, self.session)
        self.logger.info(TAG, "Director created", extra=f"id={director.id}")
        return DirectorResponse.from_model(director)

    async def update(self, id: UUID, data: DirectorUpdate) -> DirectorResponse:
        director = await self.director_repository.get_by_id(id, self.session)
        if director is None:
            raise DirectorNotFoundException(id)
        director = await self.director_repository.update(
            director, data.model_dump(exclude_unset=True), self.session
        )
        return DirectorResponse.from_model(director)

    async def delete(self, id: UUID) -> None:
        director = await self.director_repository.get_by_id(id, self.session)
        if director is None:
            raise DirectorNotFoundException(id)
        await self.director_repository.delete(director, self.session)
        self.logger.info(TAG, "Director deleted", extra=f"id={id}")

    # ── cas 2: cross-resource filter ──────────────────────────────────────────

    async def get_all_for_actor(
        self, actor_id: UUID, limit: int = 20, offset: int = 0
    ) -> list[DirectorResponse]:
        """Directors an actor has worked with (joins through movie_cast → movies)."""
        directors = await self.director_repository.find_all_by_actor(
            actor_id, self.session, limit=limit, offset=offset
        )
        return [DirectorResponse.from_model(d) for d in directors]
