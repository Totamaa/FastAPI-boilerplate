from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.logs import LoggerManager
from app.modules.movie_details.exceptions import MovieDetailNotFoundException
from app.modules.movie_details.repository import MovieDetailRepository
from app.modules.movie_details.schemas import MovieDetailCreate, MovieDetailResponse
from app.modules.movies.exceptions import MovieNotFoundException
from app.modules.movies.repository import MovieRepository


class MovieDetailService:
    def __init__(
        self,
        logger: LoggerManager,
        session: AsyncSession,
        request_id: str,
        detail_repository: MovieDetailRepository,
        movie_repository: MovieRepository,
    ):
        self.tag = "SERVICE:MovieDetail"
        self.logger = logger
        self.session = session
        self.request_id = request_id
        self.detail_repository = detail_repository
        self.movie_repository = movie_repository

    async def upsert(self, movie_id: UUID, data: MovieDetailCreate) -> MovieDetailResponse:
        movie = await self.movie_repository.get_by_id(id=movie_id, db=self.session)
        if not movie:
            raise MovieNotFoundException(id=movie_id)

        self.logger.info(
            tag=self.tag,
            message=f"Upserting detail for movie_id={movie_id}",
            extra=self.request_id,
        )
        detail_data = data.model_dump(exclude_none=True)
        detail = await self.detail_repository.upsert(
            movie_id=movie_id,
            data=detail_data,
            db=self.session,
        )
        return MovieDetailResponse.from_model(detail)

    async def get_by_movie_id(self, movie_id: UUID) -> MovieDetailResponse:
        detail = await self.detail_repository.get_by_movie_id(
            movie_id=movie_id,
            db=self.session,
        )
        if not detail:
            raise MovieDetailNotFoundException(movie_id=movie_id)
        return MovieDetailResponse.from_model(detail)
