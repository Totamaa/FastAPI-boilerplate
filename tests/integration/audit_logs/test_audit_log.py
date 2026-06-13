import pytest
from sqlalchemy import func, select, text

from app.modules.audit_logs.model import AuditLogModel
from tests.integration.builders import user_payload

pytestmark = pytest.mark.integration

BASE = "/api/v1/auth"


async def _login(client, user):
    r = await client.post(BASE + "/login", data={"username": user.email, "password": "Testpass1!"})
    return r


async def _audit_rows(db_session, action: str) -> list[AuditLogModel]:
    result = await db_session.execute(select(AuditLogModel).where(AuditLogModel.action == action))
    return list(result.scalars().all())


class TestAuditLogCreation:
    async def test_login_creates_auth_login_row(self, client, test_user, db_session):
        await _login(client, test_user)

        rows = await _audit_rows(db_session, "auth.login")
        assert len(rows) == 1
        assert rows[0].actor_id == test_user.id
        assert rows[0].target_id == test_user.id

    async def test_login_stores_ip_and_user_agent(self, client, test_user, db_session):
        await _login(client, test_user)

        rows = await _audit_rows(db_session, "auth.login")
        assert rows[0].ip is not None
        assert rows[0].user_agent is not None

    async def test_logout_creates_auth_logout_row(self, client, test_user, db_session):
        await _login(client, test_user)
        await client.post(BASE + "/logout")

        rows = await _audit_rows(db_session, "auth.logout")
        assert len(rows) == 1
        assert rows[0].actor_id == test_user.id

    async def test_logout_all_creates_auth_logout_all_row(self, client, test_user, db_session):
        r = await _login(client, test_user)
        token = r.json()["access_token"]
        await client.post(BASE + "/logout-all", headers={"Authorization": f"Bearer {token}"})

        rows = await _audit_rows(db_session, "auth.logout_all")
        assert len(rows) == 1
        assert rows[0].actor_id == test_user.id

    async def test_register_creates_user_created_row(self, client, db_session):
        await client.post(BASE + "/register", json=user_payload())

        rows = await _audit_rows(db_session, "user.created")
        assert len(rows) == 1
        assert rows[0].target_type == "user"
        assert rows[0].target_id is not None
        assert rows[0].diff is None

    async def test_revoke_session_creates_security_row(self, client, test_user, db_session):
        r = await _login(client, test_user)
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        sessions_r = await client.get(BASE + "/sessions", headers=headers)
        family_id = sessions_r.json()[0]["family_id"]

        await client.delete(f"{BASE}/sessions/{family_id}", headers=headers)

        rows = await _audit_rows(db_session, "security.session_revoked")
        assert len(rows) == 1
        assert rows[0].actor_id == test_user.id
        assert str(rows[0].target_id) == family_id

    async def test_token_theft_creates_security_row(self, client, test_user, db_session):
        r = await _login(client, test_user)
        original_rt = r.cookies.get("refresh_token")

        # Consume the token (rotation — original is now marked used)
        await client.post(BASE + "/refresh", cookies={"refresh_token": original_rt})

        # Replay the used token — triggers theft detection
        await client.post(BASE + "/refresh", cookies={"refresh_token": original_rt})

        rows = await _audit_rows(db_session, "security.token_theft")
        assert len(rows) == 1
        assert rows[0].actor_id == test_user.id


class TestAuditLogImmutability:
    async def test_update_is_silently_ignored(self, client, test_user, db_session):
        await _login(client, test_user)
        row = (await _audit_rows(db_session, "auth.login"))[0]

        await db_session.execute(
            text("UPDATE audit_logs SET action = 'hacked' WHERE id = :id"),
            {"id": row.id},
        )

        await db_session.refresh(row)
        assert row.action == "auth.login"

    async def test_delete_is_silently_ignored(self, client, test_user, db_session):
        await _login(client, test_user)

        count_before = (
            await db_session.execute(select(func.count()).select_from(AuditLogModel))
        ).scalar()

        await db_session.execute(text("DELETE FROM audit_logs"))

        count_after = (
            await db_session.execute(select(func.count()).select_from(AuditLogModel))
        ).scalar()

        assert count_after == count_before
