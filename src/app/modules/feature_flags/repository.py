import hashlib
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.feature_flags.model import FeatureFlagModel
from app.modules.feature_flags.schemas import FeatureFlagResponse


class FeatureFlagRepository:
    async def get_all(self, db: AsyncSession) -> list[FeatureFlagModel]:
        result = await db.execute(select(FeatureFlagModel).order_by(FeatureFlagModel.key))
        return list(result.scalars().all())

    async def get_by_key(self, key: str, db: AsyncSession) -> FeatureFlagModel | None:
        result = await db.execute(select(FeatureFlagModel).where(FeatureFlagModel.key == key))
        return result.scalar_one_or_none()

    async def create(self, flag: FeatureFlagModel, db: AsyncSession) -> FeatureFlagModel:
        db.add(flag)
        await db.flush()
        return flag

    async def update(
        self, flag: FeatureFlagModel, data: dict, db: AsyncSession
    ) -> FeatureFlagModel:
        for field, value in data.items():
            setattr(flag, field, value)
        await db.flush()
        return flag

    async def hard_delete(self, key: str, db: AsyncSession) -> bool:
        result = await db.execute(delete(FeatureFlagModel).where(FeatureFlagModel.key == key))
        await db.flush()
        return result.rowcount > 0

    @staticmethod
    def is_enabled_for(flag: FeatureFlagResponse, user_id: UUID | None) -> bool:
        if not flag.enabled:
            return False
        if user_id is not None and user_id in flag.allowed_user_ids:
            return True
        if user_id is not None:
            h = int(hashlib.md5(f"{user_id}{flag.key}".encode()).hexdigest(), 16)  # noqa: S324
            return h % 100 < flag.rollout_percentage
        # No user_id: only allow if flag is globally enabled (100% rollout = kill switch behaviour)
        return flag.rollout_percentage >= 100
