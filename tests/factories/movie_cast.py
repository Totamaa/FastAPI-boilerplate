from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.movie_cast.model import MovieCastModel

fake = Faker()


class MovieCastFactory:
    @staticmethod
    async def create(session: AsyncSession, movie_id, actor_id, **kwargs) -> MovieCastModel:
        entry = MovieCastModel(
            movie_id=movie_id,
            actor_id=actor_id,
            role_name=kwargs.get("role_name", fake.word().title()),
            billing_order=kwargs.get("billing_order", fake.random_int(min=1, max=10)),
            is_lead=kwargs.get("is_lead", False),
        )
        session.add(entry)
        await session.flush()
        return entry
