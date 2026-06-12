from sqlalchemy import Column, Date, String, Text
from sqlalchemy.orm import relationship

from app.modules.base.model import BaseModel


class DirectorModel(BaseModel):
    __tablename__ = "directors"

    full_name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=True)
    nationality = Column(String(100), nullable=True)
    biography = Column(Text, nullable=True)

    movies = relationship("MovieModel", back_populates="director")
