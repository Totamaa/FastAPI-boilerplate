import pytest

pytestmark = pytest.mark.integration
LOGIN = "/api/v1/auth/login"
REFRESH = "/api/v1/auth/refresh"


class TestRefreshAuth:
    async def test_no_cookie_401(self, client):
        r = await client.post(REFRESH)
        assert r.status_code == 401

    async def test_invalid_cookie_value_401(self, client):
        client.cookies.set("refresh_token", "completely-invalid-value")
        r = await client.post(REFRESH)
        assert r.status_code == 401

    async def test_expired_refresh_token_401(self, client, test_user, db_session):
        from datetime import UTC, datetime, timedelta

        from app.modules.tokens.repository import TokenRepository

        repo = TokenRepository()
        family = await repo.create_family(test_user.id, None, None, db_session)
        past = datetime.now(UTC) - timedelta(days=1)
        raw, _ = await repo.create_token(family.id, None, past, db_session)
        await db_session.flush()

        client.cookies.set("refresh_token", raw)
        r = await client.post(REFRESH)
        assert r.status_code == 401

    async def test_theft_detection_revokes_family(self, client, test_user):
        # Login → capture old RT → rotate → replay old RT → 401
        await client.post(LOGIN, data={"username": test_user.email, "password": "Testpass1!"})
        old_rt = client.cookies.get("refresh_token")
        await client.post(REFRESH)  # rotation: old_rt is now consumed
        client.cookies.set("refresh_token", old_rt)
        r = await client.post(REFRESH)
        assert r.status_code == 401

    async def test_after_theft_detection_new_rt_also_fails(self, client, test_user):
        # After family is revoked by theft detection, the new RT from the rotation is also dead
        await client.post(LOGIN, data={"username": test_user.email, "password": "Testpass1!"})
        old_rt = client.cookies.get("refresh_token")
        r_rotate = await client.post(REFRESH)
        new_rt = r_rotate.cookies.get("refresh_token")

        # Trigger theft with old RT
        client.cookies.set("refresh_token", old_rt)
        await client.post(REFRESH)  # revokes family

        # New RT from the rotation should now also fail (family revoked)
        client.cookies.set("refresh_token", new_rt)
        r = await client.post(REFRESH)
        assert r.status_code == 401

    async def test_revoked_family_401(self, client, test_user):
        await client.post(LOGIN, data={"username": test_user.email, "password": "Testpass1!"})
        await client.post("/api/v1/auth/logout")
        r = await client.post(REFRESH)
        assert r.status_code == 401
