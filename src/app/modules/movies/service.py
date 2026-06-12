from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.logs import LoggerManager
from app.modules.directors.exceptions import DirectorNotFoundException
from app.modules.directors.model import DirectorModel
from app.modules.genres.exceptions import GenreNotFoundException
from app.modules.genres.repository import GenreRepository
from app.modules.movie_cast.repository import MovieCastRepository
from app.modules.movies.enums import MovieStatus
from app.modules.movies.exceptions import MovieNotFoundException
from app.modules.movies.model import MovieModel
from app.modules.movies.repository import MovieRepository
from app.modules.movies.schemas import (
    MovieCreate,
    MovieDetailedResponse,
    MovieResponse,
    MovieUpdate,
)
from app.modules.reviews.repository import ReviewRepository


class MovieService:
    def __init__(
        self,
        logger: LoggerManager,
        session: AsyncSession,
        request_id: str,
        movie_repository: MovieRepository,
        genre_repository: GenreRepository,
        review_repository: ReviewRepository,
        cast_repository: MovieCastRepository,
    ):
        self.tag = "SERVICE:Movie"
        self.logger = logger
        self.session = session
        self.request_id = request_id
        self.movie_repository = movie_repository
        self.genre_repository = genre_repository
        self.review_repository = review_repository
        self.cast_repository = cast_repository

    async def _validate_director(self, director_id: UUID) -> None:
        result = await self.session.execute(
            select(DirectorModel).where(DirectorModel.id == director_id)
        )
        if result.scalar_one_or_none() is None:
            raise DirectorNotFoundException(id=director_id)

    async def _fetch_genres(self, genre_ids: list[UUID]) -> list:
        genres = []
        for genre_id in genre_ids:
            genre = await self.genre_repository.get_by_id(id=genre_id, db=self.session)
            if genre is None:
                raise GenreNotFoundException(genre_id)
            genres.append(genre)
        return genres

    async def get_all(
        self,
        status: MovieStatus | None = None,
        release_year: int | None = None,
        director_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MovieResponse]:
        movies = await self.movie_repository.get_all(
            db=self.session,
            status=status,
            release_year=release_year,
            director_id=director_id,
            limit=limit,
            offset=offset,
        )
        return [MovieResponse.from_model(m) for m in movies]

    async def get_by_id(self, id: UUID) -> MovieResponse:
        movie = await self.movie_repository.get_by_id(id=id, db=self.session)
        if not movie:
            raise MovieNotFoundException(id=id)
        return MovieResponse.from_model(movie)

    async def get_detailed(self, id: UUID) -> MovieDetailedResponse:
        movie = await self.movie_repository.get_detailed(id=id, db=self.session)
        if not movie:
            raise MovieNotFoundException(id=id)
        return MovieDetailedResponse.from_model(movie)

    async def create(self, data: MovieCreate) -> MovieResponse:
        self.logger.info(
            tag=self.tag,
            message=f"Creating movie title={data.title}",
            extra=self.request_id,
        )
        if data.director_id is not None:
            await self._validate_director(data.director_id)

        genres = await self._fetch_genres(data.genre_ids)

        movie = MovieModel(
            title=data.title,
            release_year=data.release_year,
            duration_minutes=data.duration_minutes,
            language=data.language,
            status=data.status,
            director_id=data.director_id,
        )
        # Set genres before add+flush so SQLAlchemy never lazy-loads the attribute
        movie.genres = genres
        await self.movie_repository.create(movie=movie, db=self.session)
        return MovieResponse.from_model(movie)

    async def update(self, id: UUID, data: MovieUpdate) -> MovieResponse:
        movie = await self.movie_repository.get_by_id(id=id, db=self.session)
        if not movie:
            raise MovieNotFoundException(id=id)

        if data.director_id is not None:
            await self._validate_director(data.director_id)

        update_data = data.model_dump(exclude_none=True, exclude={"genre_ids"})
        await self.movie_repository.update(movie=movie, data=update_data, db=self.session)

        if data.genre_ids is not None:
            genres = await self._fetch_genres(data.genre_ids)
            # Refresh the genres attribute so SQLAlchemy knows it's loaded (lazy="raise" guard)
            await self.session.refresh(movie, attribute_names=["genres"])
            movie.genres = genres
            await self.session.flush()

        self.logger.info(
            tag=self.tag,
            message=f"Updated movie id={id}",
            extra=self.request_id,
        )
        return MovieResponse.from_model(movie)

    async def delete(self, id: UUID) -> None:
        movie = await self.movie_repository.get_by_id(id=id, db=self.session)
        if not movie:
            raise MovieNotFoundException(id=id)
        self.logger.info(
            tag=self.tag,
            message=f"Deleting movie id={id}",
            extra=self.request_id,
        )
        await self.review_repository.soft_delete_by_movie(movie_id=id, db=self.session)
        await self.cast_repository.soft_delete_by_movie(movie_id=id, db=self.session)
        await self.movie_repository.delete(movie=movie, db=self.session)

    async def restore(self, id: UUID) -> MovieResponse:
        movie = await self.movie_repository.restore(id=id, db=self.session)
        if not movie:
            raise MovieNotFoundException(id=id)
        self.logger.info(
            tag=self.tag,
            message=f"Restored movie id={id}",
            extra=self.request_id,
        )
        return MovieResponse.from_model(movie)
