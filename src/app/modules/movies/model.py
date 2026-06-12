from sqlalchemy import Column, Enum, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.modules.associations.movie_genres import movie_genres
from app.modules.base.model import BaseModel
from app.modules.movies.enums import MovieStatus


class MovieModel(BaseModel):
    __tablename__ = "movies"

    title = Column(String(500), nullable=False)
    release_year = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    language = Column(String(5), nullable=True)
    status = Column(
        Enum(
            MovieStatus,
            native_enum=False,
            name="movie_status",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=MovieStatus.RELEASED,
    )
    avg_rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=False, default=0)

    director_id = Column(
        UUID(as_uuid=True), ForeignKey("directors.id", ondelete="SET NULL"), nullable=True
    )

    director = relationship("DirectorModel", back_populates="movies")
    detail = relationship(
        "MovieDetailModel",
        back_populates="movie",
        uselist=False,
        passive_deletes=True,
    )
    genres = relationship("GenreModel", secondary=movie_genres, back_populates="movies")
    cast = relationship("MovieCastModel", back_populates="movie", passive_deletes=True)
    reviews = relationship("ReviewModel", back_populates="movie", passive_deletes=True)

    __table_args__ = (
        Index("ix_movies_director_id", "director_id"),
        Index("ix_movies_release_year", "release_year"),
        Index("ix_movies_status", "status"),
    )
