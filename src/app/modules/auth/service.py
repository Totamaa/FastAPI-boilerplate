from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Request, Response

from app.core.config.logs import LoggerManager
from app.core.config.settings import get_settings
from app.core.security.jwt_lib import create_access_token
from app.modules.audit_logs.enums import AuditAction
from app.modules.audit_logs.service import AuditLogService
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


def _ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _ua(request: Request) -> str | None:
    return request.headers.get("user-agent")


class AuthService:
    def __init__(
        self,
        logger: LoggerManager,
        user_service: UserService,
        token_repo: TokenRepository,
        audit_log_service: AuditLogService,
    ) -> None:
        self.tag = "SERVICE:Auth"
        self.logger = logger
        self.user_service = user_service
        self.token_repo = token_repo
        self.audit_log_service = audit_log_service

    async def register(self, data: UserRegister) -> UserResponse:
        user = await self.user_service.register(data)
        self.logger.info(self.tag, f"Registered user id={user.id}")
        return UserResponse.from_model(user)

    async def login(self, data: UserLogin, response: Response, request: Request) -> TokenResponse:
        user = await self.user_service.authenticate(data)
        db = self.user_service.session

        settings = get_settings()
        expires_at = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

        user_agent = _ua(request)
        ip_address = _ip(request)

        family = await self.token_repo.create_family(user.id, user_agent, ip_address, db)
        raw_rt, _ = await self.token_repo.create_token(
            family_id=family.id,
            parent_id=None,
            expires_at=expires_at,
            db=db,
        )

        _set_rt_cookie(response, raw_rt)
        await self.audit_log_service.record(
            action=AuditAction.AUTH_LOGIN,
            actor_id=user.id,
            target_type="user",
            target_id=user.id,
            ip=ip_address,
            user_agent=user_agent,
        )
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
            # Theft: already-used token replayed — revoke the whole family.
            # Fetch family first to retrieve user_id for the audit log.
            family = await self.token_repo.get_family(token.family_id, db, include_revoked=True)
            await self.token_repo.revoke_family(token.family_id, db)
            actor_id = UUID(str(family.user_id)) if family else None
            await self.audit_log_service.record(
                action=AuditAction.SECURITY_TOKEN_THEFT,
                actor_id=actor_id,
                target_type="token_family",
                target_id=token.family_id,
                ip=_ip(request),
                user_agent=_ua(request),
                extra={"family_id": str(token.family_id)},
            )
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
                family = await self.token_repo.get_family(token.family_id, db)
                await self.token_repo.revoke_family(token.family_id, db)
                actor_id = UUID(str(family.user_id)) if family else None
                await self.audit_log_service.record(
                    action=AuditAction.AUTH_LOGOUT,
                    actor_id=actor_id,
                    target_type="token_family",
                    target_id=token.family_id,
                    ip=_ip(request),
                    user_agent=_ua(request),
                )
                self.logger.info(self.tag, f"Logged out family={token.family_id}")

        _clear_rt_cookie(response)

    async def logout_all(
        self, current_user: UserModel, response: Response, request: Request
    ) -> None:
        db = self.user_service.session
        await self.token_repo.revoke_all_user_families(current_user.id, db)
        _clear_rt_cookie(response)
        await self.audit_log_service.record(
            action=AuditAction.AUTH_LOGOUT_ALL,
            actor_id=current_user.id,
            target_type="user",
            target_id=current_user.id,
            ip=_ip(request),
            user_agent=_ua(request),
        )
        self.logger.info(self.tag, f"Logged out all sessions for user id={current_user.id}")

    async def get_sessions(self, current_user: UserModel) -> list[SessionResponse]:
        db = self.user_service.session
        families = await self.token_repo.get_active_families(current_user.id, db)
        return [SessionResponse.from_model(f) for f in families]

    async def revoke_session(
        self, family_id: UUID, current_user: UserModel, request: Request
    ) -> None:
        db = self.user_service.session
        family = await self.token_repo.get_family(family_id, db)
        if family is None or family.user_id != current_user.id:
            raise RefreshTokenFamilyOwnershipException()
        await self.token_repo.revoke_family(family_id, db)
        await self.audit_log_service.record(
            action=AuditAction.SECURITY_SESSION_REVOKED,
            actor_id=current_user.id,
            target_type="token_family",
            target_id=family_id,
            ip=_ip(request),
            user_agent=_ua(request),
        )
        self.logger.info(
            self.tag, f"Revoked session family={family_id} for user id={current_user.id}"
        )
