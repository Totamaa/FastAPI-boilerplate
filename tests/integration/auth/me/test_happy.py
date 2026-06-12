import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/auth/me"


class TestAuthMeHappy:
    async def test_returns_200(self, user_client):
        assert (await user_client.get(BASE)).status_code == 200

    async def test_returns_own_profile(self, user_client, test_user):
        r = await user_client.get(BASE)
        d = r.json()
        assert d["email"] == test_user.email
        assert "id" in d and "is_active" in d and "is_admin" in d

    async def test_returns_correct_user_id(self, user_client, test_user, second_user):
        r = await user_client.get(BASE)
        assert r.json()["id"] == str(test_user.id)
