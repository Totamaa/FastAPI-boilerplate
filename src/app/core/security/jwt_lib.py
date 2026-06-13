from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import BaseModel, Field, ValidationError

from app.core.config.settings import get_settings
from app.core.errors.exceptions.auth import JWTExpiredException, JWTInvalidSignatureException


class TokenPayload(BaseModel):
    sub: str = Field(..., description="User ID (UUID as string)")
    exp: int = Field(..., description="Expiry timestamp")
    type: str = Field(..., pattern=r"^(access|refresh)$")


def create_access_token(user_id: UUID) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    settings = get_settings()
    try:
        payload_dict = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except ExpiredSignatureError as exc:
        raise JWTExpiredException() from exc
    except JWTError as exc:
        raise JWTInvalidSignatureException() from exc
    try:
        return TokenPayload.model_validate(payload_dict)
    except ValidationError as exc:
        raise JWTInvalidSignatureException() from exc
