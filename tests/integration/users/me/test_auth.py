import time

import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/users/me"


class TestUsersMeAuth:
    async def test_no_token_401(self, client):
        assert (await client.get(BASE)).status_code == 401

    async def test_invalid_token_401(self, client):
        assert (
            await client.get(BASE, headers={"Authorization": "Bearer bad.token"})
        ).status_code == 401

    async def test_expired_token_401(self, client, settings, test_user):
        from jose import jwt

        payload = {"sub": str(test_user.id), "type": "access", "exp": int(time.time()) - 60}
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        assert (
            await client.get(BASE, headers={"Authorization": f"Bearer {token}"})
        ).status_code == 401

    async def test_api_key_not_accepted_401(self, admin_client):
        assert (await admin_client.get(BASE)).status_code == 401
