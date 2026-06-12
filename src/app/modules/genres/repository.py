from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.genres.model import GenreModel


class GenreRepository:
    async def get_all(self, db: AsyncSession, limit: int = 20, offset: int = 0) -> list[GenreModel]:
        result = await db.execute(
            select(GenreModel).order_by(GenreModel.name).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_id(self, id: UUID, db: AsyncSession) -> GenreModel | None:
        result = await db.execute(select(GenreModel).where(GenreModel.id == id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str, db: AsyncSession) -> GenreModel | None:
        result = await db.execute(select(GenreModel).where(GenreModel.slug == slug))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str, db: AsyncSession) -> GenreModel | None:
        result = await db.execute(select(GenreModel).where(GenreModel.name == name))
        return result.scalar_one_or_none()

    async def create(self, genre: GenreModel, db: AsyncSession) -> GenreModel:
        db.add(genre)
        await db.flush()
        await db.refresh(genre)
        return genre

    async def delete(self, genre: GenreModel, db: AsyncSession) -> None:
        genre.deleted_at = datetime.now(UTC)
        await db.flush()

    async def restore(self, id: UUID, db: AsyncSession) -> GenreModel | None:
        stmt = select(GenreModel).where(GenreModel.id == id).execution_options(include_deleted=True)
        result = await db.execute(stmt)
        entity = result.scalar_one_or_none()
        if entity is not None:
            entity.deleted_at = None
            await db.flush()
        return entity
