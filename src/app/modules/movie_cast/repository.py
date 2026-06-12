from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.movie_cast.model import MovieCastModel


class MovieCastRepository:
    async def get_by_movie(
        self,
        movie_id: UUID,
        db: AsyncSession,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MovieCastModel]:
        stmt = (
            select(MovieCastModel)
            .where(MovieCastModel.movie_id == movie_id)
            .options(
                selectinload(MovieCastModel.actor),
                selectinload(MovieCastModel.movie),
            )
            .order_by(MovieCastModel.billing_order)
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(
        self,
        id: UUID,
        db: AsyncSession,
    ) -> MovieCastModel | None:
        stmt = select(MovieCastModel).where(MovieCastModel.id == id)
        result = await db.execute(stmt)
        return result.scalars().one_or_none()

    async def get_by_movie_and_actor(
        self,
        movie_id: UUID,
        actor_id: UUID,
        db: AsyncSession,
    ) -> MovieCastModel | None:
        stmt = select(MovieCastModel).where(
            MovieCastModel.movie_id == movie_id,
            MovieCastModel.actor_id == actor_id,
        )
        result = await db.execute(stmt)
        return result.scalars().one_or_none()

    async def create(
        self,
        entry: MovieCastModel,
        db: AsyncSession,
    ) -> MovieCastModel:
        db.add(entry)
        await db.flush()
        return entry

    async def update(
        self,
        entry: MovieCastModel,
        data: dict,
        db: AsyncSession,
    ) -> MovieCastModel:
        for key, value in data.items():
            setattr(entry, key, value)
        await db.flush()
        return entry

    async def delete(
        self,
        entry: MovieCastModel,
        db: AsyncSession,
    ) -> None:
        entry.deleted_at = datetime.now(UTC)
        await db.flush()

    async def restore(self, id: UUID, db: AsyncSession) -> MovieCastModel | None:
        stmt = (
            select(MovieCastModel)
            .where(MovieCastModel.id == id)
            .execution_options(include_deleted=True)
        )
        result = await db.execute(stmt)
        entity = result.scalar_one_or_none()
        if entity is not None:
            entity.deleted_at = None
            await db.flush()
        return entity

    async def soft_delete_by_movie(self, movie_id: UUID, db: AsyncSession) -> None:
        stmt = (
            update(MovieCastModel)
            .where(MovieCastModel.movie_id == movie_id)
            .values(deleted_at=datetime.now(UTC))
        )
        await db.execute(stmt)
        await db.flush()

    async def soft_delete_by_actor(self, actor_id: UUID, db: AsyncSession) -> None:
        stmt = (
            update(MovieCastModel)
            .where(MovieCastModel.actor_id == actor_id)
            .values(deleted_at=datetime.now(UTC))
        )
        await db.execute(stmt)
        await db.flush()
