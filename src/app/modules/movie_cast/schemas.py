from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CastEntryCreate(BaseModel):
    movie_id: UUID
    actor_id: UUID
    role_name: str = Field(..., min_length=1, max_length=255)
    billing_order: int = Field(..., ge=1, le=100)
    is_lead: bool = False


class CastEntryUpdate(BaseModel):
    role_name: str | None = Field(None, min_length=1, max_length=255)
    billing_order: int | None = Field(None, ge=1, le=100)
    is_lead: bool | None = None


class ActorBriefResponse(BaseModel):
    id: UUID
    full_name: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> "ActorBriefResponse":
        return cls(id=model.id, full_name=model.full_name)


class MovieBriefResponse(BaseModel):
    id: UUID
    title: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> "MovieBriefResponse":
        return cls(id=model.id, title=model.title)


class CastEntryResponse(BaseModel):
    id: UUID
    movie_id: UUID
    actor_id: UUID
    role_name: str
    billing_order: int
    is_lead: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, entry) -> "CastEntryResponse":
        return cls(
            id=entry.id,
            movie_id=entry.movie_id,
            actor_id=entry.actor_id,
            role_name=entry.role_name,
            billing_order=entry.billing_order,
            is_lead=entry.is_lead,
            created_at=entry.created_at,
        )


class CastEntryDetailedResponse(CastEntryResponse):
    actor: ActorBriefResponse
    movie: MovieBriefResponse

    @classmethod
    def from_model(cls, entry) -> "CastEntryDetailedResponse":
        return cls(
            id=entry.id,
            movie_id=entry.movie_id,
            actor_id=entry.actor_id,
            role_name=entry.role_name,
            billing_order=entry.billing_order,
            is_lead=entry.is_lead,
            created_at=entry.created_at,
            actor=ActorBriefResponse.from_model(entry.actor),
            movie=MovieBriefResponse.from_model(entry.movie),
        )
