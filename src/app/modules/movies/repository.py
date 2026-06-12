from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.movie_cast.model import MovieCastModel
from app.modules.movies.enums import MovieStatus
from app.modules.movies.model import MovieModel


class MovieRepository:
    async def get_all(
        self,
        db: AsyncSession,
        status: MovieStatus | None = None,
        release_year: int | None = None,
        director_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MovieModel]:
        stmt = select(MovieModel)
        if status is not None:
            stmt = stmt.where(MovieModel.status == status)
        if release_year is not None:
            stmt = stmt.where(MovieModel.release_year == release_year)
        if director_id is not None:
            stmt = stmt.where(MovieModel.director_id == director_id)
        stmt = stmt.order_by(MovieModel.release_year.desc()).limit(limit).offset(offset)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(
        self,
        id: UUID,
        db: AsyncSession,
    ) -> MovieModel | None:
        stmt = select(MovieModel).where(MovieModel.id == id)
        result = await db.execute(stmt)
        return result.scalars().one_or_none()

    async def get_detailed(
        self,
        id: UUID,
        db: AsyncSession,
    ) -> MovieModel | None:
        stmt = (
            select(MovieModel)
            .where(MovieModel.id == id)
            .options(
                selectinload(MovieModel.director),
                selectinload(MovieModel.detail),
                selectinload(MovieModel.genres),
                selectinload(MovieModel.cast).selectinload(MovieCastModel.actor),
            )
        )
        result = await db.execute(stmt)
        return result.scalars().one_or_none()

    async def create(
        self,
        movie: MovieModel,
        db: AsyncSession,
    ) -> MovieModel:
        db.add(movie)
        await db.flush()
        return movie

    async def update(
        self,
        movie: MovieModel,
        data: dict,
        db: AsyncSession,
    ) -> MovieModel:
        for key, value in data.items():
            setattr(movie, key, value)
        await db.flush()
        return movie

    async def delete(
        self,
        movie: MovieModel,
        db: AsyncSession,
    ) -> None:
        await db.delete(movie)
        await db.flush()

    async def update_stats(
        self,
        movie_id: UUID,
        avg_rating: float | None,
        review_count: int,
        db: AsyncSession,
    ) -> None:
        stmt = (
            update(MovieModel)
            .where(MovieModel.id == movie_id)
            .values(avg_rating=avg_rating, review_count=review_count)
        )
        await db.execute(stmt)
        await db.flush()
