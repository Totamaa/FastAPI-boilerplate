from uuid import UUID

from app.core.security.jwt_lib import create_access_token


def bearer_headers(user_id: UUID) -> dict[str, str]:
    token = create_access_token(user_id)
    return {"Authorization": f"Bearer {token}"}


def api_key_headers(api_key: str) -> dict[str, str]:
    return {"X-API-Key": api_key}
