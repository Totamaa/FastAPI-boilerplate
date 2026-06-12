from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.api.dependencies.auth import get_current_user, verify_api_key
from app.modules.users.dependencies import get_user_service
from app.modules.users.model import UserModel
from app.modules.users.schemas import UserResponse
from app.modules.users.service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_my_profile(
    current_user: UserModel = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    id: UUID,
    _: None = Depends(verify_api_key),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await service.get_by_id(id=id)
