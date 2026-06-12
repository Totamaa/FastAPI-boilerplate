from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.movies.enums import MovieStatus


class ActorInMovieResponse(BaseModel):
    """Actor + role info embedded in a movie response."""

    actor_id: UUID
    full_name: str
    nationality: str | None
    role_name: str
    billing_order: int
    is_lead: bool

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_cast_entry(cls, entry) -> "ActorInMovieResponse":
        return cls(
            actor_id=entry.actor_id,
            full_name=entry.actor.full_name,
            nationality=entry.actor.nationality,
            role_name=entry.role_name,
            billing_order=entry.billing_order,
            is_lead=entry.is_lead,
        )


class GenreBriefResponse(BaseModel):
    id: UUID
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> "GenreBriefResponse":
        return cls(id=model.id, name=model.name, slug=model.slug)


class DirectorBriefResponse(BaseModel):
    id: UUID
    full_name: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> "DirectorBriefResponse":
        return cls(id=model.id, full_name=model.full_name)


class MovieDetailBriefResponse(BaseModel):
    synopsis: str | None = None
    budget_usd: int | None = None
    box_office_usd: int | None = None
    awards_count: int | None = None
    country: str | None = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> "MovieDetailBriefResponse":
        return cls(
            synopsis=model.synopsis,
            budget_usd=model.budget_usd,
            box_office_usd=model.box_office_usd,
            awards_count=model.awards_count,
            country=model.country,
        )


class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    release_year: int = Field(..., ge=1888, le=2100)
    duration_minutes: int | None = Field(None, ge=1, le=600)
    language: str | None = Field(None, max_length=5)
    status: MovieStatus = Field(MovieStatus.RELEASED)
    director_id: UUID | None = Field(None)
    genre_ids: list[UUID] = Field(default_factory=list)


class MovieUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    release_year: int | None = Field(None, ge=1888, le=2100)
    duration_minutes: int | None = Field(None, ge=1, le=600)
    language: str | None = Field(None, max_length=5)
    status: MovieStatus | None = Field(None)
    director_id: UUID | None = None
    genre_ids: list[UUID] | None = None


class MovieResponse(BaseModel):
    id: UUID
    title: str
    release_year: int
    duration_minutes: int | None
    language: str | None
    status: MovieStatus
    avg_rating: float | None
    review_count: int
    director_id: UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, movie) -> "MovieResponse":
        return cls(
            id=movie.id,
            title=movie.title,
            release_year=movie.release_year,
            duration_minutes=movie.duration_minutes,
            language=movie.language,
            status=movie.status,
            avg_rating=movie.avg_rating,
            review_count=movie.review_count,
            director_id=movie.director_id,
            created_at=movie.created_at,
        )


class MovieDetailedResponse(MovieResponse):
    director: DirectorBriefResponse | None
    genres: list[GenreBriefResponse]
    cast: list[ActorInMovieResponse]
    detail: MovieDetailBriefResponse | None

    @classmethod
    def from_model(cls, movie) -> "MovieDetailedResponse":
        return cls(
            id=movie.id,
            title=movie.title,
            release_year=movie.release_year,
            duration_minutes=movie.duration_minutes,
            language=movie.language,
            status=movie.status,
            avg_rating=movie.avg_rating,
            review_count=movie.review_count,
            director_id=movie.director_id,
            created_at=movie.created_at,
            director=DirectorBriefResponse.from_model(movie.director) if movie.director else None,
            genres=[GenreBriefResponse.from_model(g) for g in (movie.genres or [])],
            cast=sorted(
                [ActorInMovieResponse.from_cast_entry(c) for c in (movie.cast or [])],
                key=lambda x: x.billing_order,
            ),
            detail=MovieDetailBriefResponse.from_model(movie.detail) if movie.detail else None,
        )
