from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from app.modules.feature_flags.model import FeatureFlagModel


class FeatureFlagCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=200, pattern=r"^[a-z0-9_:.-]+$")
    enabled: bool = Field(False)
    rollout_percentage: int = Field(0, ge=0, le=100)
    allowed_user_ids: list[UUID] = Field(default_factory=list)
    description: str | None = Field(None, max_length=500)


class FeatureFlagUpdate(BaseModel):
    enabled: bool | None = None
    rollout_percentage: int | None = Field(None, ge=0, le=100)
    allowed_user_ids: list[UUID] | None = None
    description: str | None = None


class FeatureFlagResponse(BaseModel):
    key: str
    enabled: bool
    rollout_percentage: int
    allowed_user_ids: list[UUID]
    description: str | None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model: FeatureFlagModel) -> FeatureFlagResponse:
        return cls(
            key=model.key,
            enabled=model.enabled,
            rollout_percentage=model.rollout_percentage,
            allowed_user_ids=model.allowed_user_ids or [],
            description=model.description,
            updated_at=model.updated_at,
        )
