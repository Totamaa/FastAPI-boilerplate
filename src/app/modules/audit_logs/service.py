from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit_logs.enums import AuditAction
from app.modules.audit_logs.model import AuditLogModel
from app.modules.audit_logs.repository import AuditLogRepository


class AuditLogService:
    def __init__(self, session: AsyncSession, repo: AuditLogRepository) -> None:
        self.session = session
        self.repo = repo

    async def record(
        self,
        action: AuditAction,
        actor_id: UUID | None = None,
        target_type: str | None = None,
        target_id: UUID | None = None,
        diff: dict | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
        extra: dict | None = None,
    ) -> None:
        audit_log = AuditLogModel(
            actor_id=actor_id,
            action=str(action),
            target_type=target_type,
            target_id=target_id,
            diff=diff,
            ip=ip,
            user_agent=user_agent,
            extra=extra,
        )
        await self.repo.create(audit_log, self.session)
