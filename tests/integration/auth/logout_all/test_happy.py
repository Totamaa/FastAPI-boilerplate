import pytest

pytestmark = pytest.mark.integration
LOGIN = "/api/v1/auth/login"
LOGOUT_ALL = "/api/v1/auth/logout-all"
REFRESH = "/api/v1/auth/refresh"


class TestLogoutAllHappy:
    async def test_logout_all_returns_204(self, user_client):
        r = await user_client.post(LOGOUT_ALL)
        assert r.status_code == 204

    async def test_logout_all_clears_cookie(self, user_client):
        await user_client.post(LOGOUT_ALL)
        assert user_client.cookies.get("refresh_token") is None

    async def test_logout_all_revokes_all_sessions(self, client, test_user, db_session):
        from datetime import UTC, datetime, timedelta

        from app.core.security.jwt_lib import create_access_token
        from app.modules.tokens.repository import TokenRepository

        # Create 2 families directly in DB (simulating 2 login sessions)
        repo = TokenRepository()
        expires = datetime.now(UTC) + timedelta(days=30)
        fam1 = await repo.create_family(test_user.id, "agent-1", "1.1.1.1", db_session)
        raw1, _ = await repo.create_token(fam1.id, None, expires, db_session)
        fam2 = await repo.create_family(test_user.id, "agent-2", "2.2.2.2", db_session)
        raw2, _ = await repo.create_token(fam2.id, None, expires, db_session)
        await db_session.flush()

        token = create_access_token(test_user.id)
        await client.post(LOGOUT_ALL, headers={"Authorization": f"Bearer {token}"})

        # Both sessions should now be revoked
        client.cookies.set("refresh_token", raw1)
        assert (await client.post(REFRESH)).status_code == 401
        client.cookies.set("refresh_token", raw2)
        assert (await client.post(REFRESH)).status_code == 401

    async def test_logout_all_requires_auth(self, client):
        r = await client.post(LOGOUT_ALL)
        assert r.status_code == 401
