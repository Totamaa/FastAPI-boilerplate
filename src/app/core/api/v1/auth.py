from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.api.dependencies.auth import get_current_user
from app.modules.auth.dependencies import get_auth_service
from app.modules.auth.service import AuthService
from app.modules.users.model import UserModel
from app.modules.users.schemas import TokenResponse, UserLogin, UserRegister, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    return await service.register(data)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    # OAuth2 spec uses "username" — we treat it as email
    return await service.login(UserLogin(email=form.username, password=form.password))


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def me(
    current_user: UserModel = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.from_model(current_user)
