from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.movie_details.model import MovieDetailModel


class MovieDetailRepository:
    async def get_by_movie_id(
        self,
        movie_id: UUID,
        db: AsyncSession,
    ) -> MovieDetailModel | None:
        stmt = select(MovieDetailModel).where(MovieDetailModel.movie_id == movie_id)
        result = await db.execute(stmt)
        return result.scalars().one_or_none()

    async def upsert(
        self,
        movie_id: UUID,
        data: dict,
        db: AsyncSession,
    ) -> MovieDetailModel:
        existing = await self.get_by_movie_id(movie_id=movie_id, db=db)
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
            await db.flush()
            return existing
        detail = MovieDetailModel(movie_id=movie_id, **data)
        db.add(detail)
        await db.flush()
        return detail
