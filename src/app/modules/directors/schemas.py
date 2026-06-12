from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from app.modules.directors.model import DirectorModel


class MovieBriefResponse(BaseModel):
    id: UUID
    title: str = Field(..., max_length=500)
    release_year: int
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, movie) -> MovieBriefResponse:
        return cls(id=movie.id, title=movie.title, release_year=movie.release_year)


class DirectorCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    birth_date: date | None = Field(None)
    nationality: str | None = Field(None, max_length=100)
    biography: str | None = Field(None)

    def to_model(self) -> DirectorModel:
        from app.modules.directors.model import DirectorModel

        return DirectorModel(
            full_name=self.full_name,
            birth_date=self.birth_date,
            nationality=self.nationality,
            biography=self.biography,
        )


class DirectorUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    birth_date: date | None = Field(None)
    nationality: str | None = Field(None, max_length=100)
    biography: str | None = Field(None)


class DirectorResponse(BaseModel):
    id: UUID
    full_name: str
    birth_date: date | None
    nationality: str | None
    biography: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> DirectorResponse:
        return cls(
            id=model.id,
            full_name=model.full_name,
            birth_date=model.birth_date,
            nationality=model.nationality,
            biography=model.biography,
            created_at=model.created_at,
        )


class DirectorWithMoviesResponse(DirectorResponse):
    movies: list[MovieBriefResponse] = Field(default_factory=list)

    @classmethod
    def from_model(cls, model) -> DirectorWithMoviesResponse:
        return cls(
            id=model.id,
            full_name=model.full_name,
            birth_date=model.birth_date,
            nationality=model.nationality,
            biography=model.biography,
            created_at=model.created_at,
            movies=[MovieBriefResponse.from_model(m) for m in (model.movies or [])],
        )
