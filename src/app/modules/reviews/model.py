from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.modules.base.model import BaseModel


class ReviewModel(BaseModel):
    __tablename__ = "reviews"

    # 1-N depuis user + 1-N depuis movie
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    movie_id = Column(
        UUID(as_uuid=True), ForeignKey("movies.id", ondelete="CASCADE"), nullable=False
    )
    rating = Column(Integer, nullable=False)  # 1–10
    title = Column(String(255), nullable=True)
    body = Column(Text, nullable=True)
    contains_spoilers = Column(Boolean, nullable=False, default=False)

    author = relationship("UserModel", back_populates="reviews")
    movie = relationship("MovieModel", back_populates="reviews")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 10", name="ck_reviews_rating_range"),
        UniqueConstraint("user_id", "movie_id", name="uq_reviews_user_movie"),
        Index("ix_reviews_movie_id", "movie_id"),
        Index("ix_reviews_user_id", "user_id"),
    )
