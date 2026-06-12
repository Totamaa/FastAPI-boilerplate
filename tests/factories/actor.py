from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.actors.model import ActorModel

fake = Faker()


class ActorFactory:
    @staticmethod
    async def create(session: AsyncSession, **kwargs) -> ActorModel:
        actor = ActorModel(
            full_name=kwargs.get("full_name", fake.name()),
            nationality=kwargs.get("nationality", fake.country()),
        )
        session.add(actor)
        await session.flush()
        return actor
