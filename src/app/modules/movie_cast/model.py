from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.modules.base.model import BaseModel


class MovieCastModel(BaseModel):
    __tablename__ = "movie_cast"

    # N-N avec data: Movie <-> Actor avec role_name, billing_order, is_lead
    movie_id = Column(
        UUID(as_uuid=True), ForeignKey("movies.id", ondelete="CASCADE"), nullable=False
    )
    actor_id = Column(
        UUID(as_uuid=True), ForeignKey("actors.id", ondelete="CASCADE"), nullable=False
    )
    role_name = Column(String(255), nullable=False)
    billing_order = Column(Integer, nullable=False)  # position au générique
    is_lead = Column(Boolean, nullable=False, default=False)

    movie = relationship("MovieModel", back_populates="cast")
    actor = relationship("ActorModel", back_populates="cast_entries")

    __table_args__ = (
        UniqueConstraint("movie_id", "actor_id", name="uq_movie_cast_movie_actor"),
        Index("ix_movie_cast_movie_id", "movie_id"),
        Index("ix_movie_cast_actor_id", "actor_id"),
    )
