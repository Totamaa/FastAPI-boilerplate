from fastapi import APIRouter, Depends
from fastapi import status as http_status

from app.core.api.dependencies.auth import verify_api_key
from app.modules.feature_flags.dependencies import get_feature_flag_service
from app.modules.feature_flags.schemas import (
    FeatureFlagCreate,
    FeatureFlagResponse,
    FeatureFlagUpdate,
)
from app.modules.feature_flags.service import FeatureFlagService

router = APIRouter()


@router.get(
    "/",
    response_model=list[FeatureFlagResponse],
    status_code=http_status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)],
)
async def list_feature_flags(
    service: FeatureFlagService = Depends(get_feature_flag_service),
) -> list[FeatureFlagResponse]:
    return await service.get_all()


@router.post(
    "/",
    response_model=FeatureFlagResponse,
    status_code=http_status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
)
async def create_feature_flag(
    payload: FeatureFlagCreate,
    service: FeatureFlagService = Depends(get_feature_flag_service),
) -> FeatureFlagResponse:
    return await service.create(payload)


@router.patch(
    "/{key}",
    response_model=FeatureFlagResponse,
    status_code=http_status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)],
)
async def update_feature_flag(
    key: str,
    payload: FeatureFlagUpdate,
    service: FeatureFlagService = Depends(get_feature_flag_service),
) -> FeatureFlagResponse:
    return await service.update(key, payload)


@router.delete(
    "/{key}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_api_key)],
)
async def delete_feature_flag(
    key: str,
    service: FeatureFlagService = Depends(get_feature_flag_service),
) -> None:
    await service.delete(key)
