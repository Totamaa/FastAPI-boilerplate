from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MovieDetailCreate(BaseModel):
    synopsis: str | None = Field(None)
    budget_usd: int | None = Field(None, ge=0, description="Budget in USD")
    box_office_usd: int | None = Field(None, ge=0)
    awards_count: int | None = Field(None, ge=0)
    country: str | None = Field(None, max_length=100)


class MovieDetailUpdate(BaseModel):
    synopsis: str | None = Field(None)
    budget_usd: int | None = Field(None, ge=0, description="Budget in USD")
    box_office_usd: int | None = Field(None, ge=0)
    awards_count: int | None = Field(None, ge=0)
    country: str | None = Field(None, max_length=100)


class MovieDetailResponse(BaseModel):
    id: UUID
    movie_id: UUID
    synopsis: str | None
    budget_usd: int | None
    box_office_usd: int | None
    awards_count: int | None
    country: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> "MovieDetailResponse":
        return cls(
            id=model.id,
            movie_id=model.movie_id,
            synopsis=model.synopsis,
            budget_usd=model.budget_usd,
            box_office_usd=model.box_office_usd,
            awards_count=model.awards_count,
            country=model.country,
            created_at=model.created_at,
        )
