from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.db import get_session
from app.core.api.dependencies.request_id import get_request_id
from app.core.config.logs import get_logger
from app.modules.audit_logs.dependencies import get_audit_log_service
from app.modules.audit_logs.service import AuditLogService
from app.modules.reviews.repository import ReviewRepository
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService


def get_user_repository() -> UserRepository:
    return UserRepository()


def _get_review_repository() -> ReviewRepository:
    return ReviewRepository()


def get_user_service(
    logger=Depends(get_logger),
    session: AsyncSession = Depends(get_session),
    request_id: str = Depends(get_request_id),
    user_repo: UserRepository = Depends(get_user_repository),
    review_repo: ReviewRepository = Depends(_get_review_repository),
    audit_log_service: AuditLogService = Depends(get_audit_log_service),
) -> UserService:
    return UserService(
        logger=logger,
        session=session,
        request_id=request_id,
        user_repository=user_repo,
        review_repository=review_repo,
        audit_log_service=audit_log_service,
    )
