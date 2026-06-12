from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from app.modules.actors.model import ActorModel


class MovieInActorResponse(BaseModel):
    """The movie + role info when listing an actor's filmography."""

    movie_id: UUID
    movie_title: str
    role_name: str
    billing_order: int
    is_lead: bool
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_cast_entry(cls, entry) -> MovieInActorResponse:
        return cls(
            movie_id=entry.movie_id,
            movie_title=entry.movie.title,
            role_name=entry.role_name,
            billing_order=entry.billing_order,
            is_lead=entry.is_lead,
        )


class ActorCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    birth_date: date | None = Field(None)
    nationality: str | None = Field(None, max_length=100)
    biography: str | None = Field(None)

    def to_model(self) -> ActorModel:
        from app.modules.actors.model import ActorModel

        return ActorModel(
            full_name=self.full_name,
            birth_date=self.birth_date,
            nationality=self.nationality,
            biography=self.biography,
        )


class ActorUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    birth_date: date | None = Field(None)
    nationality: str | None = Field(None, max_length=100)
    biography: str | None = Field(None)


class ActorResponse(BaseModel):
    id: UUID
    full_name: str
    birth_date: date | None
    nationality: str | None
    biography: str | None
    created_at: datetime
    # cas 3 — optional include: None when ?include=movies not requested
    filmography: list[MovieInActorResponse] | None = None
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model, *, include_movies: bool = False) -> ActorResponse:
        return cls(
            id=model.id,
            full_name=model.full_name,
            birth_date=model.birth_date,
            nationality=model.nationality,
            biography=model.biography,
            created_at=model.created_at,
            filmography=(
                [MovieInActorResponse.from_cast_entry(e) for e in (model.cast_entries or [])]
                if include_movies
                else None
            ),
        )
