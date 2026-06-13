import pytest

pytestmark = pytest.mark.integration
LOGIN = "/api/v1/auth/login"
LOGOUT = "/api/v1/auth/logout"
REFRESH = "/api/v1/auth/refresh"


class TestLogoutHappy:
    async def test_logout_returns_204(self, client, test_user):
        await client.post(LOGIN, data={"username": test_user.email, "password": "Testpass1!"})
        r = await client.post(LOGOUT)
        assert r.status_code == 204

    async def test_logout_clears_cookie(self, client, test_user):
        await client.post(LOGIN, data={"username": test_user.email, "password": "Testpass1!"})
        await client.post(LOGOUT)
        assert client.cookies.get("refresh_token") is None

    async def test_logout_invalidates_refresh_token(self, client, test_user):
        await client.post(LOGIN, data={"username": test_user.email, "password": "Testpass1!"})
        rt = client.cookies.get("refresh_token")
        await client.post(LOGOUT)
        # Re-inject the old cookie manually and try to refresh
        client.cookies.set("refresh_token", rt)
        r = await client.post(REFRESH)
        assert r.status_code == 401

    async def test_logout_without_cookie_is_graceful(self, client):
        # Logout with no active session should still return 204
        r = await client.post(LOGOUT)
        assert r.status_code == 204
