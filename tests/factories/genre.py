from uuid import uuid4

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.genres.model import GenreModel

fake = Faker()


class GenreFactory:
    @staticmethod
    async def create(session: AsyncSession, **kwargs) -> GenreModel:
        name = kwargs.get("name", f"{fake.word().capitalize()}-{uuid4().hex[:6]}")
        genre = GenreModel(
            name=name,
            slug=kwargs.get("slug", name.lower().replace(" ", "-")),
        )
        session.add(genre)
        await session.flush()
        return genre
