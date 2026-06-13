from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.modules.base.model import BaseModel


class RefreshTokenFamilyModel(BaseModel):
    __tablename__ = "refresh_token_families"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(45), nullable=True)

    user = relationship("UserModel", back_populates="token_families")
    tokens = relationship(
        "RefreshTokenModel",
        back_populates="family",
        cascade="all, delete-orphan",
    )


class RefreshTokenModel(BaseModel):
    __tablename__ = "refresh_tokens"

    token_hash = Column(String(64), nullable=False, unique=True, index=True)
    family_id = Column(
        UUID(as_uuid=True),
        ForeignKey("refresh_token_families.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("refresh_tokens.id", ondelete="SET NULL"),
        nullable=True,
    )
    used_at = Column(DateTime(timezone=True), nullable=True, default=None)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    family = relationship("RefreshTokenFamilyModel", back_populates="tokens")
