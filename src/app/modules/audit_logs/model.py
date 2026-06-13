from sqlalchemy import Column, Index, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.modules.base.model import BaseModel


class AuditLogModel(BaseModel):
    __tablename__ = "audit_logs"

    actor_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(Text, nullable=False)
    target_type = Column(Text, nullable=True)
    target_id = Column(UUID(as_uuid=True), nullable=True)
    diff = Column(JSONB, nullable=True)
    ip = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
    extra = Column("metadata", JSONB, nullable=True)

    __table_args__ = (
        Index("ix_audit_logs_actor_id", "actor_id"),
        Index("ix_audit_logs_target", "target_type", "target_id"),
        Index("ix_audit_logs_created_at", "created_at"),
    )
