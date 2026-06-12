import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/auth/login"


class TestLoginHappy:
    async def test_valid_credentials_return_200(self, client, test_user):
        r = await client.post(BASE, data={"username": test_user.email, "password": "Testpass1!"})
        assert r.status_code == 200

    async def test_response_has_both_tokens(self, client, test_user):
        r = await client.post(BASE, data={"username": test_user.email, "password": "Testpass1!"})
        d = r.json()
        assert "access_token" in d and "refresh_token" in d

    async def test_token_type_is_bearer(self, client, test_user):
        r = await client.post(BASE, data={"username": test_user.email, "password": "Testpass1!"})
        assert r.json()["token_type"] == "bearer"

    async def test_access_token_usable_on_protected_route(self, client, test_user):
        r = await client.post(BASE, data={"username": test_user.email, "password": "Testpass1!"})
        token = r.json()["access_token"]
        me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
