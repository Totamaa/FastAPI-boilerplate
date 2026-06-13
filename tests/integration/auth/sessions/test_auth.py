import uuid

import pytest

pytestmark = pytest.mark.integration
SESSIONS = "/api/v1/auth/sessions"


class TestSessionsAuth:
    async def test_list_sessions_requires_auth(self, client):
        r = await client.get(SESSIONS)
        assert r.status_code == 401

    async def test_delete_session_requires_auth(self, client):
        r = await client.delete(f"{SESSIONS}/{uuid.uuid4()}")
        assert r.status_code == 401
