from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    movie_id: UUID
    rating: int = Field(..., ge=1, le=10)
    title: str | None = Field(None, max_length=255)
    body: str | None = Field(None)
    contains_spoilers: bool = Field(False)


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=10)
    title: str | None = Field(None, max_length=255)
    body: str | None = Field(None)
    contains_spoilers: bool | None = None


class ReviewAuthorBrief(BaseModel):
    id: UUID
    email: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> "ReviewAuthorBrief":
        return cls(id=model.id, email=model.email)


class ReviewResponse(BaseModel):
    id: UUID
    user_id: UUID
    movie_id: UUID
    rating: int
    title: str | None
    body: str | None
    contains_spoilers: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, review) -> "ReviewResponse":
        return cls(
            id=review.id,
            user_id=review.user_id,
            movie_id=review.movie_id,
            rating=review.rating,
            title=review.title,
            body=review.body,
            contains_spoilers=review.contains_spoilers,
            created_at=review.created_at,
        )


class ReviewDetailedResponse(ReviewResponse):
    author: ReviewAuthorBrief

    @classmethod
    def from_model(cls, review) -> "ReviewDetailedResponse":
        return cls(
            id=review.id,
            user_id=review.user_id,
            movie_id=review.movie_id,
            rating=review.rating,
            title=review.title,
            body=review.body,
            contains_spoilers=review.contains_spoilers,
            created_at=review.created_at,
            author=ReviewAuthorBrief.from_model(review.author),
        )
