from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.logs import LoggerManager
from app.modules.genres.exceptions import GenreConflictException, GenreNotFoundException
from app.modules.genres.repository import GenreRepository
from app.modules.genres.schemas import GenreCreate, GenreResponse

TAG = "genres"


class GenreService:
    def __init__(
        self,
        logger: LoggerManager,
        session: AsyncSession,
        request_id: str,
        genre_repository: GenreRepository,
    ):
        self.logger = logger
        self.session = session
        self.request_id = request_id
        self.genre_repository = genre_repository

    async def get_all(self, limit: int = 20, offset: int = 0) -> list[GenreResponse]:
        self.logger.info(TAG, "Fetching all genres", extra=f"request_id={self.request_id}")
        genres = await self.genre_repository.get_all(self.session, limit=limit, offset=offset)
        return [GenreResponse.from_model(g) for g in genres]

    async def get_by_id(self, id: UUID) -> GenreResponse:
        self.logger.info(
            TAG, "Fetching genre by id", extra=f"id={id}, request_id={self.request_id}"
        )
        genre = await self.genre_repository.get_by_id(id, self.session)
        if genre is None:
            raise GenreNotFoundException(id)
        return GenreResponse.from_model(genre)

    async def create(self, data: GenreCreate) -> GenreResponse:
        self.logger.info(TAG, "Creating genre", extra=f"request_id={self.request_id}")
        if await self.genre_repository.get_by_slug(data.slug, self.session):
            raise GenreConflictException("slug", data.slug)
        if await self.genre_repository.get_by_name(data.name, self.session):
            raise GenreConflictException("name", data.name)
        genre = data.to_model()
        genre = await self.genre_repository.create(genre, self.session)
        self.logger.info(TAG, "Genre created", extra=f"id={genre.id}, request_id={self.request_id}")
        return GenreResponse.from_model(genre)

    async def delete(self, id: UUID) -> None:
        self.logger.info(TAG, "Deleting genre", extra=f"id={id}, request_id={self.request_id}")
        genre = await self.genre_repository.get_by_id(id, self.session)
        if genre is None:
            raise GenreNotFoundException(id)
        await self.genre_repository.delete(genre, self.session)
        self.logger.info(TAG, "Genre deleted", extra=f"id={id}, request_id={self.request_id}")
