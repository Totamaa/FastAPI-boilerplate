import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/users"


class TestUsersGetHappy:
    async def test_returns_user_by_id(self, admin_client, test_user):
        r = await admin_client.get(f"{BASE}/{test_user.id}")
        assert r.status_code == 200

    async def test_response_has_expected_fields(self, admin_client, test_user):
        r = await admin_client.get(f"{BASE}/{test_user.id}")
        d = r.json()
        assert d["id"] == str(test_user.id)
        assert d["email"] == test_user.email
        assert "is_active" in d and "is_admin" in d
