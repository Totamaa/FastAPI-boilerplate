from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from app.modules.genres.model import GenreModel


class GenreCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = Field(None)

    def to_model(self) -> GenreModel:
        from app.modules.genres.model import GenreModel

        return GenreModel(
            name=self.name,
            slug=self.slug,
            description=self.description,
        )


class GenreUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    slug: str | None = Field(None, min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = Field(None)


class GenreResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> GenreResponse:
        return cls(
            id=model.id,
            name=model.name,
            slug=model.slug,
            description=model.description,
        )
