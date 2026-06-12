from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.directors.model import DirectorModel
from app.modules.movie_cast.model import MovieCastModel
from app.modules.movies.model import MovieModel


class DirectorRepository:
    # ── standard CRUD ────────────────────────────────────────────────────────

    async def get_all(
        self, db: AsyncSession, limit: int = 20, offset: int = 0
    ) -> list[DirectorModel]:
        result = await db.execute(
            select(DirectorModel).order_by(DirectorModel.full_name).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_id(self, id: UUID, db: AsyncSession) -> DirectorModel | None:
        result = await db.execute(select(DirectorModel).where(DirectorModel.id == id))
        return result.scalar_one_or_none()

    async def create(self, director: DirectorModel, db: AsyncSession) -> DirectorModel:
        db.add(director)
        await db.flush()
        await db.refresh(director)
        return director

    async def update(self, director: DirectorModel, data: dict, db: AsyncSession) -> DirectorModel:
        for key, value in data.items():
            setattr(director, key, value)
        await db.flush()
        await db.refresh(director)
        return director

    async def delete(self, director: DirectorModel, db: AsyncSession) -> None:
        director.deleted_at = datetime.now(UTC)
        await db.flush()

    async def restore(self, id: UUID, db: AsyncSession) -> DirectorModel | None:
        stmt = (
            select(DirectorModel)
            .where(DirectorModel.id == id)
            .execution_options(include_deleted=True)
        )
        result = await db.execute(stmt)
        entity = result.scalar_one_or_none()
        if entity is not None:
            entity.deleted_at = None
            await db.flush()
        return entity

    # ── cas 2: cross-resource filter ──────────────────────────────────────────

    async def find_all_by_actor(
        self,
        actor_id: UUID,
        db: AsyncSession,
        limit: int = 20,
        offset: int = 0,
    ) -> list[DirectorModel]:
        """Directors an actor has worked with.

        JOIN path: directors ← movies ← movie_cast → actor
        """
        result = await db.execute(
            select(DirectorModel)
            .join(MovieModel, MovieModel.director_id == DirectorModel.id)
            .join(MovieCastModel, MovieCastModel.movie_id == MovieModel.id)
            .where(MovieCastModel.actor_id == actor_id)
            .distinct()
            .order_by(DirectorModel.full_name)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
