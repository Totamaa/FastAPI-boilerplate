from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.feature_flags.model import FeatureFlagModel


class FeatureFlagFactory:
    @staticmethod
    async def create(
        session: AsyncSession,
        key: str = "test:feature",
        enabled: bool = True,
        rollout_percentage: int = 100,
        allowed_user_ids: list | None = None,
        description: str | None = None,
    ) -> FeatureFlagModel:
        flag = FeatureFlagModel(
            key=key,
            enabled=enabled,
            rollout_percentage=rollout_percentage,
            allowed_user_ids=allowed_user_ids or [],
            description=description,
        )
        session.add(flag)
        await session.flush()
        return flag
