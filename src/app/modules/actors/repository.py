from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.actors.model import ActorModel
from app.modules.movie_cast.model import MovieCastModel


class ActorRepository:
    async def get_all(self, db: AsyncSession, limit: int = 20, offset: int = 0) -> list[ActorModel]:
        result = await db.execute(
            select(ActorModel).order_by(ActorModel.full_name).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_id(self, id: UUID, db: AsyncSession) -> ActorModel | None:
        result = await db.execute(select(ActorModel).where(ActorModel.id == id))
        return result.scalar_one_or_none()

    async def create(self, actor: ActorModel, db: AsyncSession) -> ActorModel:
        db.add(actor)
        await db.flush()
        await db.refresh(actor)
        return actor

    async def update(self, actor: ActorModel, data: dict, db: AsyncSession) -> ActorModel:
        for key, value in data.items():
            setattr(actor, key, value)
        await db.flush()
        await db.refresh(actor)
        return actor

    async def delete(self, actor: ActorModel, db: AsyncSession) -> None:
        await db.delete(actor)
        await db.flush()

    async def get_with_cast(self, id: UUID, db: AsyncSession) -> ActorModel | None:
        result = await db.execute(
            select(ActorModel)
            .options(selectinload(ActorModel.cast_entries).selectinload(MovieCastModel.movie))
            .where(ActorModel.id == id)
        )
        return result.scalar_one_or_none()
