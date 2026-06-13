from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache.feature_flags import get_all_cached, invalidate, set_all_cached
from app.core.config.logs import LoggerManager
from app.modules.feature_flags.exceptions import (
    FeatureFlagConflictException,
    FeatureFlagNotFoundException,
)
from app.modules.feature_flags.model import FeatureFlagModel
from app.modules.feature_flags.repository import FeatureFlagRepository
from app.modules.feature_flags.schemas import (
    FeatureFlagCreate,
    FeatureFlagResponse,
    FeatureFlagUpdate,
)

TAG = "feature_flags"


class FeatureFlagService:
    def __init__(
        self,
        logger: LoggerManager,
        session: AsyncSession,
        request_id: str,
        repo: FeatureFlagRepository,
    ) -> None:
        self.logger = logger
        self.session = session
        self.request_id = request_id
        self.repo = repo

    async def get_all(self) -> list[FeatureFlagResponse]:
        cached = await get_all_cached()
        if cached is not None:
            return [FeatureFlagResponse(**item) for item in cached]
        flags = await self.repo.get_all(self.session)
        responses = [FeatureFlagResponse.from_model(f) for f in flags]
        await set_all_cached([r.model_dump(mode="json") for r in responses])
        return responses

    async def get_by_key(self, key: str) -> FeatureFlagResponse:
        flag = await self.repo.get_by_key(key, self.session)
        if flag is None:
            raise FeatureFlagNotFoundException(key)
        return FeatureFlagResponse.from_model(flag)

    async def is_feature_enabled(self, key: str, user_id: UUID | None = None) -> bool:
        cached = await get_all_cached()
        if cached is not None:
            raw = next((item for item in cached if item["key"] == key), None)
            if raw is None:
                return False
            return FeatureFlagRepository.is_enabled_for(FeatureFlagResponse(**raw), user_id)
        flag = await self.repo.get_by_key(key, self.session)
        if flag is None:
            return False
        return FeatureFlagRepository.is_enabled_for(FeatureFlagResponse.from_model(flag), user_id)

    async def create(self, data: FeatureFlagCreate) -> FeatureFlagResponse:
        existing = await self.repo.get_by_key(data.key, self.session)
        if existing is not None:
            raise FeatureFlagConflictException(data.key)
        flag = FeatureFlagModel(
            key=data.key,
            enabled=data.enabled,
            rollout_percentage=data.rollout_percentage,
            allowed_user_ids=data.allowed_user_ids,
            description=data.description,
        )
        flag = await self.repo.create(flag, self.session)
        await invalidate()
        self.logger.info(
            TAG, "Feature flag created", extra=f"key={data.key}, request_id={self.request_id}"
        )
        return FeatureFlagResponse.from_model(flag)

    async def update(self, key: str, data: FeatureFlagUpdate) -> FeatureFlagResponse:
        flag = await self.repo.get_by_key(key, self.session)
        if flag is None:
            raise FeatureFlagNotFoundException(key)
        update_data = data.model_dump(exclude_none=True)
        flag = await self.repo.update(flag, update_data, self.session)
        await invalidate()
        self.logger.info(
            TAG, "Feature flag updated", extra=f"key={key}, request_id={self.request_id}"
        )
        return FeatureFlagResponse.from_model(flag)

    async def delete(self, key: str) -> None:
        deleted = await self.repo.hard_delete(key, self.session)
        if not deleted:
            raise FeatureFlagNotFoundException(key)
        await invalidate()
        self.logger.info(
            TAG, "Feature flag deleted", extra=f"key={key}, request_id={self.request_id}"
        )
