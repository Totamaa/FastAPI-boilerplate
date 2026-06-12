from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.directors.model import DirectorModel

fake = Faker()


class DirectorFactory:
    @staticmethod
    async def create(session: AsyncSession, **kwargs) -> DirectorModel:
        director = DirectorModel(
            full_name=kwargs.get("full_name", fake.name()),
            nationality=kwargs.get("nationality", fake.country()),
        )
        session.add(director)
        await session.flush()
        return director
