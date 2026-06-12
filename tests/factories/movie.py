from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.movies.model import MovieModel

fake = Faker()


class MovieFactory:
    @staticmethod
    async def create(session: AsyncSession, **kwargs) -> MovieModel:
        movie = MovieModel(
            title=kwargs.get("title", " ".join(fake.words(3)).title()),
            release_year=kwargs.get("release_year", fake.random_int(min=1950, max=2024)),
            status=kwargs.get("status", "released"),
            director_id=kwargs.get("director_id"),
        )
        session.add(movie)
        await session.flush()
        return movie
