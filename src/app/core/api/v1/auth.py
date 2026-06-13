from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.api.dependencies.auth import get_current_user
from app.modules.auth.dependencies import get_auth_service
from app.modules.auth.service import AuthService
from app.modules.tokens.schemas import SessionResponse
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
    request: Request,
    response: Response,
    form: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await service.login(
        UserLogin(email=form.username, password=form.password), response, request
    )


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await service.refresh(response, request)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> None:
    await service.logout(request, response)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    request: Request,
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> None:
    await service.logout_all(current_user, response, request)


@router.get("/sessions", response_model=list[SessionResponse], status_code=status.HTTP_200_OK)
async def get_sessions(
    current_user: UserModel = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> list[SessionResponse]:
    return await service.get_sessions(current_user)


@router.delete("/sessions/{family_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session(
    family_id: UUID,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> None:
    await service.revoke_session(family_id, current_user, request)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def me(
    current_user: UserModel = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.from_model(current_user)
