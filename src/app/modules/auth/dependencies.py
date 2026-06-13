from fastapi import Depends

from app.core.config.logs import get_logger
from app.modules.audit_logs.dependencies import get_audit_log_service
from app.modules.audit_logs.service import AuditLogService
from app.modules.auth.service import AuthService
from app.modules.tokens.repository import TokenRepository
from app.modules.users.dependencies import get_user_service
from app.modules.users.service import UserService


def get_token_repository() -> TokenRepository:
    return TokenRepository()


def get_auth_service(
    logger=Depends(get_logger),
    user_service: UserService = Depends(get_user_service),
    token_repo: TokenRepository = Depends(get_token_repository),
    audit_log_service: AuditLogService = Depends(get_audit_log_service),
) -> AuthService:
    return AuthService(
        logger=logger,
        user_service=user_service,
        token_repo=token_repo,
        audit_log_service=audit_log_service,
    )
