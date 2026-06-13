from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SessionResponse(BaseModel):
    family_id: UUID
    user_agent: str | None
    ip_address: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> "SessionResponse":
        return cls(
            family_id=model.id,
            user_agent=model.user_agent,
            ip_address=model.ip_address,
            created_at=model.created_at,
        )
