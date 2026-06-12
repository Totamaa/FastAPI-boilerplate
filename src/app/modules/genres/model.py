from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.modules.associations.movie_genres import movie_genres
from app.modules.base.model import BaseModel


class GenreModel(BaseModel):
    __tablename__ = "genres"

    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    movies = relationship("MovieModel", secondary=movie_genres, back_populates="genres")
