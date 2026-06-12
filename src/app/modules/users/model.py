from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from app.modules.base.model import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_admin = Column(Boolean, nullable=False, default=False)

    reviews = relationship(
        "ReviewModel", back_populates="author", passive_deletes=True
    )
