import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/auth/login"


class TestLoginHappy:
    async def test_valid_credentials_return_200(self, client, test_user):
        r = await client.post(BASE, data={"username": test_user.email, "password": "Testpass1!"})
        assert r.status_code == 200

    async def test_response_has_access_token(self, client, test_user):
        r = await client.post(BASE, data={"username": test_user.email, "password": "Testpass1!"})
        d = r.json()
        assert "access_token" in d
        assert d["token_type"] == "bearer"

    async def test_refresh_token_not_in_body(self, client, test_user):
        r = await client.post(BASE, data={"username": test_user.email, "password": "Testpass1!"})
        assert "refresh_token" not in r.json()

    async def test_refresh_token_set_as_httponly_cookie(self, client, test_user):
        r = await client.post(BASE, data={"username": test_user.email, "password": "Testpass1!"})
        assert r.cookies.get("refresh_token") is not None

    async def test_access_token_usable_on_protected_route(self, client, test_user):
        r = await client.post(BASE, data={"username": test_user.email, "password": "Testpass1!"})
        token = r.json()["access_token"]
        me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
