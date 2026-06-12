import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/auth/login"


class TestLoginAuth:
    async def test_login_is_public(self, client, test_user):
        r = await client.post(BASE, data={"username": test_user.email, "password": "Testpass1!"})
        assert r.status_code == 200

    async def test_extra_api_key_header_does_not_break_login(self, admin_client, test_user):
        r = await admin_client.post(
            BASE, data={"username": test_user.email, "password": "Testpass1!"}
        )
        assert r.status_code == 200
