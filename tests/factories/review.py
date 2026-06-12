from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reviews.model import ReviewModel

fake = Faker()


class ReviewFactory:
    @staticmethod
    async def create(
        session: AsyncSession,
        user_id,
        movie_id,
        **kwargs,
    ) -> ReviewModel:
        review = ReviewModel(
            user_id=user_id,
            movie_id=movie_id,
            rating=kwargs.get("rating", fake.random_int(min=1, max=10)),
            title=kwargs.get("title", fake.sentence(nb_words=4)),
            body=kwargs.get("body", fake.paragraph()),
            contains_spoilers=kwargs.get("contains_spoilers", False),
        )
        session.add(review)
        await session.flush()
        return review
