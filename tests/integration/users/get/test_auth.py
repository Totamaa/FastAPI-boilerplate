import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/users"


class TestUsersGetAuth:
    async def test_no_api_key_401(self, client, test_user):
        assert (await client.get(f"{BASE}/{test_user.id}")).status_code == 401

    async def test_wrong_api_key_401(self, client, test_user):
        headers = {"X-API-Key": "wrong-key"}
        assert (await client.get(f"{BASE}/{test_user.id}", headers=headers)).status_code == 401

    async def test_jwt_token_not_accepted_401(self, user_client, test_user):
        assert (await user_client.get(f"{BASE}/{test_user.id}")).status_code == 401
