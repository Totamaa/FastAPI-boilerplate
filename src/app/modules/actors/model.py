from sqlalchemy import Column, Date, String, Text
from sqlalchemy.orm import relationship

from app.modules.base.model import BaseModel


class ActorModel(BaseModel):
    __tablename__ = "actors"

    full_name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=True)
    nationality = Column(String(100), nullable=True)
    biography = Column(Text, nullable=True)

    cast_entries = relationship(
        "MovieCastModel", back_populates="actor", passive_deletes=True
    )
