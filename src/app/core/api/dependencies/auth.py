import secrets
from uuid import UUID

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.db import get_session
from app.core.config.settings import Settings, get_settings
from app.core.errors.exceptions.auth import JWTMissingSubjectException, JWTWrongTypeException
from app.core.security.jwt_lib import decode_token
from app.modules.users.model import UserModel
from app.modules.users.repository import UserRepository

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str | None = Security(_api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    if api_key is None or not secrets.compare_digest(api_key, settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )


_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(_oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> UserModel:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    # Raises JWTExpiredException or JWTInvalidSignatureException — handled by BusinessException handler
    payload = decode_token(token)

    if payload.type != "access":
        raise JWTWrongTypeException(expected="access", got=payload.type)

    try:
        user_id = UUID(payload.sub)
    except ValueError as exc:
        raise JWTMissingSubjectException() from exc

    repo = UserRepository()
    user = await repo.get_by_id(id=user_id, db=session)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive."
        )
    return user
