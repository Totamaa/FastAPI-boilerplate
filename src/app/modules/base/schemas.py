from uuid import UUID

from pydantic import BaseModel, Field


class IdResponse(BaseModel):
    id: UUID = Field(..., description="ID of the resource")
