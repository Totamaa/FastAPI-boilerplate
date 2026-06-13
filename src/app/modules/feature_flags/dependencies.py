from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.db import get_session
from app.core.api.dependencies.request_id import get_request_id
from app.core.config.logs import LoggerManager, get_logger
from app.modules.feature_flags.exceptions import FeatureDisabledException
from app.modules.feature_flags.repository import FeatureFlagRepository
from app.modules.feature_flags.service import FeatureFlagService


def get_feature_flag_repository() -> FeatureFlagRepository:
    return FeatureFlagRepository()


def get_feature_flag_service(
    logger: LoggerManager = Depends(get_logger),
    session: AsyncSession = Depends(get_session),
    request_id: str = Depends(get_request_id),
    repo: FeatureFlagRepository = Depends(get_feature_flag_repository),
) -> FeatureFlagService:
    return FeatureFlagService(
        logger=logger,
        session=session,
        request_id=request_id,
        repo=repo,
    )


def require_feature(flag_key: str) -> Depends:
    """Dependency factory — raises 503 if the named feature flag is disabled.

    Usage: dependencies=[require_feature("movies:listing_enabled")]
    """

    async def _check(service: FeatureFlagService = Depends(get_feature_flag_service)) -> None:
        if not await service.is_feature_enabled(flag_key):
            raise FeatureDisabledException(flag_key)

    return Depends(_check)
