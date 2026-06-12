from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.reviews.model import ReviewModel


class ReviewRepository:
    async def get_by_movie(
        self,
        movie_id: UUID,
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ReviewModel]:
        stmt = (
            select(ReviewModel)
            .where(ReviewModel.movie_id == movie_id)
            .options(selectinload(ReviewModel.author))
            .order_by(ReviewModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> list[ReviewModel]:
        stmt = select(ReviewModel).where(ReviewModel.user_id == user_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(
        self,
        id: UUID,
        db: AsyncSession,
    ) -> ReviewModel | None:
        stmt = select(ReviewModel).where(ReviewModel.id == id)
        result = await db.execute(stmt)
        return result.scalars().one_or_none()

    async def get_by_user_and_movie(
        self,
        user_id: UUID,
        movie_id: UUID,
        db: AsyncSession,
    ) -> ReviewModel | None:
        stmt = select(ReviewModel).where(
            ReviewModel.user_id == user_id,
            ReviewModel.movie_id == movie_id,
        )
        result = await db.execute(stmt)
        return result.scalars().one_or_none()

    async def create(
        self,
        review: ReviewModel,
        db: AsyncSession,
    ) -> ReviewModel:
        db.add(review)
        await db.flush()
        return review

    async def update(
        self,
        review: ReviewModel,
        data: dict,
        db: AsyncSession,
    ) -> ReviewModel:
        for key, value in data.items():
            setattr(review, key, value)
        await db.flush()
        return review

    async def delete(
        self,
        review: ReviewModel,
        db: AsyncSession,
    ) -> None:
        review.deleted_at = datetime.now(UTC)
        await db.flush()

    async def restore(self, id: UUID, db: AsyncSession) -> ReviewModel | None:
        stmt = (
            select(ReviewModel).where(ReviewModel.id == id).execution_options(include_deleted=True)
        )
        result = await db.execute(stmt)
        entity = result.scalar_one_or_none()
        if entity is not None:
            entity.deleted_at = None
            await db.flush()
        return entity

    async def soft_delete_by_movie(self, movie_id: UUID, db: AsyncSession) -> None:
        stmt = (
            update(ReviewModel)
            .where(ReviewModel.movie_id == movie_id)
            .values(deleted_at=datetime.now(UTC))
        )
        await db.execute(stmt)
        await db.flush()

    async def soft_delete_by_user(self, user_id: UUID, db: AsyncSession) -> None:
        stmt = (
            update(ReviewModel)
            .where(ReviewModel.user_id == user_id)
            .values(deleted_at=datetime.now(UTC))
        )
        await db.execute(stmt)
        await db.flush()

    async def compute_movie_stats(
        self,
        movie_id: UUID,
        db: AsyncSession,
    ) -> tuple[float | None, int]:
        result = await db.execute(
            select(func.avg(ReviewModel.rating), func.count(ReviewModel.id)).where(
                ReviewModel.movie_id == movie_id
            )
        )
        avg, count = result.one()
        return (float(avg) if avg is not None else None), (count or 0)
