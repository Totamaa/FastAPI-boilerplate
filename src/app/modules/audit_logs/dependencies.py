from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.db import get_session
from app.modules.audit_logs.repository import AuditLogRepository
from app.modules.audit_logs.service import AuditLogService


def get_audit_log_repository() -> AuditLogRepository:
    return AuditLogRepository()


def get_audit_log_service(
    session: AsyncSession = Depends(get_session),
    repo: AuditLogRepository = Depends(get_audit_log_repository),
) -> AuditLogService:
    return AuditLogService(session=session, repo=repo)
