import pytest

pytestmark = pytest.mark.integration
LOGIN = "/api/v1/auth/login"
REFRESH = "/api/v1/auth/refresh"
ME = "/api/v1/auth/me"


class TestRefreshHappy:
    async def test_refresh_returns_200(self, client, test_user):
        await client.post(LOGIN, data={"username": test_user.email, "password": "Testpass1!"})
        r = await client.post(REFRESH)
        assert r.status_code == 200

    async def test_refresh_response_has_access_token(self, client, test_user):
        await client.post(LOGIN, data={"username": test_user.email, "password": "Testpass1!"})
        r = await client.post(REFRESH)
        d = r.json()
        assert "access_token" in d
        assert d["token_type"] == "bearer"

    async def test_refresh_sets_new_cookie(self, client, test_user):
        await client.post(LOGIN, data={"username": test_user.email, "password": "Testpass1!"})
        old_rt = client.cookies.get("refresh_token")
        r = await client.post(REFRESH)
        new_rt = r.cookies.get("refresh_token")
        assert new_rt is not None
        assert new_rt != old_rt

    async def test_new_access_token_works_on_protected_route(self, client, test_user):
        await client.post(LOGIN, data={"username": test_user.email, "password": "Testpass1!"})
        r = await client.post(REFRESH)
        token = r.json()["access_token"]
        me = await client.get(ME, headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200

    async def test_old_refresh_token_is_invalidated(self, client, test_user):
        await client.post(LOGIN, data={"username": test_user.email, "password": "Testpass1!"})
        old_rt = client.cookies.get("refresh_token")
        await client.post(REFRESH)
        # Replay the old (now consumed) token
        client.cookies.set("refresh_token", old_rt)
        r = await client.post(REFRESH)
        assert r.status_code == 401
