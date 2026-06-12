from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.genres.model import GenreModel

fake = Faker()


class GenreFactory:
    @staticmethod
    async def create(session: AsyncSession, **kwargs) -> GenreModel:
        name = kwargs.get("name", fake.unique.word().capitalize())
        genre = GenreModel(
            name=name,
            slug=kwargs.get("slug", name.lower().replace(" ", "-")),
        )
        session.add(genre)
        await session.flush()
        return genre
