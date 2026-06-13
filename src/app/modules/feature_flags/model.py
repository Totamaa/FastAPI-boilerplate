from datetime import UTC, datetime

from sqlalchemy import ARRAY, Boolean, Column, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as pgUUID

from app.modules.base.model import PlainBase


class FeatureFlagModel(PlainBase):
    __tablename__ = "feature_flags"

    key = Column(Text, primary_key=True, nullable=False)
    enabled = Column(Boolean, nullable=False, default=False)
    rollout_percentage = Column(Integer, nullable=False, default=0)
    allowed_user_ids = Column(ARRAY(pgUUID(as_uuid=True)), nullable=False, default=list)
    description = Column(Text, nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
