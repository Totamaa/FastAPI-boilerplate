from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.model import UserModel


class UserRepository:
    async def get_by_id(
        self,
        id: UUID,
        db: AsyncSession,
    ) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.id == id)
        result = await db.execute(stmt)
        return result.scalars().one_or_none()

    async def get_by_email(
        self,
        email: str,
        db: AsyncSession,
    ) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await db.execute(stmt)
        return result.scalars().one_or_none()

    async def create(
        self,
        user: UserModel,
        db: AsyncSession,
    ) -> UserModel:
        db.add(user)
        await db.flush()
        return user

    async def update(
        self,
        user: UserModel,
        data: dict,
        db: AsyncSession,
    ) -> UserModel:
        for key, value in data.items():
            setattr(user, key, value)
        await db.flush()
        return user

    async def restore(self, id: UUID, db: AsyncSession) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.id == id).execution_options(include_deleted=True)
        result = await db.execute(stmt)
        entity = result.scalar_one_or_none()
        if entity is not None:
            entity.deleted_at = None
            await db.flush()
        return entity
