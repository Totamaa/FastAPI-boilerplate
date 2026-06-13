from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit_logs.model import AuditLogModel


class AuditLogRepository:
    async def create(self, audit_log: AuditLogModel, db: AsyncSession) -> AuditLogModel:
        db.add(audit_log)
        await db.flush()
        return audit_log
