from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Request, Response

from app.core.config.logs import LoggerManager
from app.core.config.settings import get_settings
from app.core.security.jwt_lib import create_access_token
from app.modules.tokens.exceptions import (
    RefreshTokenExpiredException,
    RefreshTokenFamilyOwnershipException,
    RefreshTokenNotFoundException,
    RefreshTokenRevokedException,
    RefreshTokenTheftException,
)
from app.modules.tokens.repository import TokenRepository
from app.modules.tokens.schemas import SessionResponse
from app.modules.users.model import UserModel
from app.modules.users.schemas import TokenResponse, UserLogin, UserRegister, UserResponse
from app.modules.users.service import UserService


def _set_rt_cookie(response: Response, raw_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key="refresh_token",
        value=raw_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "prod",
        samesite="strict",
        path="/api/v1/auth",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )


def _clear_rt_cookie(response: Response) -> None:
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")


class AuthService:
    def __init__(
        self,
        logger: LoggerManager,
        user_service: UserService,
        token_repo: TokenRepository,
    ) -> None:
        self.tag = "SERVICE:Auth"
        self.logger = logger
        self.user_service = user_service
        self.token_repo = token_repo

    async def register(self, data: UserRegister) -> UserResponse:
        user = await self.user_service.register(data)
        self.logger.info(self.tag, f"Registered user id={user.id}")
        return UserResponse.from_model(user)

    async def login(self, data: UserLogin, response: Response, request: Request) -> TokenResponse:
        user = await self.user_service.authenticate(data)
        db = self.user_service.session

        settings = get_settings()
        expires_at = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None

        family = await self.token_repo.create_family(user.id, user_agent, ip_address, db)
        raw_rt, _ = await self.token_repo.create_token(
            family_id=family.id,
            parent_id=None,
            expires_at=expires_at,
            db=db,
        )

        _set_rt_cookie(response, raw_rt)
        self.logger.info(self.tag, f"Logged in user id={user.id} family={family.id}")
        return TokenResponse(access_token=create_access_token(user.id))

    async def refresh(self, response: Response, request: Request) -> TokenResponse:
        raw_rt = request.cookies.get("refresh_token")
        if not raw_rt:
            raise RefreshTokenNotFoundException()

        db = self.user_service.session

        token = await self.token_repo.get_token_by_raw(raw_rt, db)
        if token is None:
            raise RefreshTokenNotFoundException()

        if token.used_at is not None:
            # Theft: already-used token replayed — revoke the whole family
            await self.token_repo.revoke_family(token.family_id, db)
            self.logger.error(
                self.tag, f"Token theft detected for family={token.family_id}. Family revoked."
            )
            raise RefreshTokenTheftException()

        if token.expires_at < datetime.now(UTC):
            raise RefreshTokenExpiredException()

        family = await self.token_repo.get_family(token.family_id, db, include_revoked=True)
        if family is None or family.deleted_at is not None:
            raise RefreshTokenRevokedException()

        settings = get_settings()
        new_expires_at = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

        await self.token_repo.mark_token_used(token, db)
        raw_new, _ = await self.token_repo.create_token(
            family_id=token.family_id,
            parent_id=token.id,
            expires_at=new_expires_at,
            db=db,
        )

        _set_rt_cookie(response, raw_new)
        self.logger.info(self.tag, f"Rotated RT for family={token.family_id}")

        user_id = UUID(str(family.user_id))
        return TokenResponse(access_token=create_access_token(user_id))

    async def logout(self, request: Request, response: Response) -> None:
        raw_rt = request.cookies.get("refresh_token")
        db = self.user_service.session

        if raw_rt:
            token = await self.token_repo.get_token_by_raw(raw_rt, db)
            if token is not None:
                await self.token_repo.revoke_family(token.family_id, db)
                self.logger.info(self.tag, f"Logged out family={token.family_id}")

        _clear_rt_cookie(response)

    async def logout_all(self, current_user: UserModel, response: Response) -> None:
        db = self.user_service.session
        await self.token_repo.revoke_all_user_families(current_user.id, db)
        _clear_rt_cookie(response)
        self.logger.info(self.tag, f"Logged out all sessions for user id={current_user.id}")

    async def get_sessions(self, current_user: UserModel) -> list[SessionResponse]:
        db = self.user_service.session
        families = await self.token_repo.get_active_families(current_user.id, db)
        return [SessionResponse.from_model(f) for f in families]

    async def revoke_session(self, family_id: UUID, current_user: UserModel) -> None:
        db = self.user_service.session
        family = await self.token_repo.get_family(family_id, db)
        if family is None or family.user_id != current_user.id:
            raise RefreshTokenFamilyOwnershipException()
        await self.token_repo.revoke_family(family_id, db)
        self.logger.info(
            self.tag, f"Revoked session family={family_id} for user id={current_user.id}"
        )
