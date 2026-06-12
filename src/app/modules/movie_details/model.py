from sqlalchemy import BigInteger, Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.modules.base.model import BaseModel


class MovieDetailModel(BaseModel):
    __tablename__ = "movie_details"

    # 1-1 with movies — unique constraint enforces the relationship
    movie_id = Column(
        UUID(as_uuid=True), ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    synopsis = Column(Text, nullable=True)
    budget_usd = Column(BigInteger, nullable=True)
    box_office_usd = Column(BigInteger, nullable=True)
    awards_count = Column(Integer, nullable=True, default=0)
    country = Column(String(100), nullable=True)

    movie = relationship("MovieModel", back_populates="detail")

    __table_args__ = (Index("ix_movie_details_movie_id", "movie_id"),)
