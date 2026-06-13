import pytest

pytestmark = pytest.mark.integration
SESSIONS = "/api/v1/auth/sessions"


class TestSessionsHappy:
    async def test_lists_active_sessions(self, user_client, test_user, db_session):
        from datetime import UTC, datetime, timedelta

        from app.modules.tokens.repository import TokenRepository

        repo = TokenRepository()
        expires = datetime.now(UTC) + timedelta(days=30)
        family = await repo.create_family(test_user.id, "Mozilla/5.0", "127.0.0.1", db_session)
        await repo.create_token(family.id, None, expires, db_session)
        await db_session.flush()

        r = await user_client.get(SESSIONS)
        assert r.status_code == 200
        family_ids = [s["family_id"] for s in r.json()]
        assert str(family.id) in family_ids

    async def test_session_response_shape(self, user_client, test_user, db_session):
        from datetime import UTC, datetime, timedelta

        from app.modules.tokens.repository import TokenRepository

        repo = TokenRepository()
        expires = datetime.now(UTC) + timedelta(days=30)
        family = await repo.create_family(test_user.id, "test-agent", "10.0.0.1", db_session)
        await repo.create_token(family.id, None, expires, db_session)
        await db_session.flush()

        r = await user_client.get(SESSIONS)
        s = next(s for s in r.json() if s["family_id"] == str(family.id))
        assert "family_id" in s
        assert "user_agent" in s
        assert "ip_address" in s
        assert "created_at" in s

    async def test_revoked_sessions_not_listed(self, user_client, test_user, db_session):
        from datetime import UTC, datetime, timedelta

        from app.modules.tokens.repository import TokenRepository

        repo = TokenRepository()
        expires = datetime.now(UTC) + timedelta(days=30)
        family = await repo.create_family(test_user.id, "old-agent", "1.2.3.4", db_session)
        await repo.create_token(family.id, None, expires, db_session)
        await repo.revoke_family(family.id, db_session)
        await db_session.flush()

        r = await user_client.get(SESSIONS)
        family_ids = [s["family_id"] for s in r.json()]
        assert str(family.id) not in family_ids

    async def test_delete_session_returns_204(self, user_client, test_user, db_session):
        from datetime import UTC, datetime, timedelta

        from app.modules.tokens.repository import TokenRepository

        repo = TokenRepository()
        expires = datetime.now(UTC) + timedelta(days=30)
        family = await repo.create_family(test_user.id, "agent", "1.1.1.1", db_session)
        await repo.create_token(family.id, None, expires, db_session)
        await db_session.flush()

        r = await user_client.delete(f"{SESSIONS}/{family.id}")
        assert r.status_code == 204

    async def test_delete_session_revokes_rt(self, client, user_client, test_user, db_session):
        from datetime import UTC, datetime, timedelta

        from app.modules.tokens.repository import TokenRepository

        repo = TokenRepository()
        expires = datetime.now(UTC) + timedelta(days=30)
        family = await repo.create_family(test_user.id, "agent", "1.1.1.1", db_session)
        raw, _ = await repo.create_token(family.id, None, expires, db_session)
        await db_session.flush()

        await user_client.delete(f"{SESSIONS}/{family.id}")

        client.cookies.set("refresh_token", raw)
        assert (await client.post("/api/v1/auth/refresh")).status_code == 401

    async def test_delete_other_users_session_404(self, user_client, second_user, db_session):
        from datetime import UTC, datetime, timedelta

        from app.modules.tokens.repository import TokenRepository

        repo = TokenRepository()
        expires = datetime.now(UTC) + timedelta(days=30)
        family = await repo.create_family(second_user.id, "agent", "1.1.1.1", db_session)
        await repo.create_token(family.id, None, expires, db_session)
        await db_session.flush()

        r = await user_client.delete(f"{SESSIONS}/{family.id}")
        assert r.status_code == 404
