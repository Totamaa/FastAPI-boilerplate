import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/users"


class TestUsersDeleteAuth:
    async def test_no_api_key_401(self, client, test_user):
        assert (await client.delete(f"{BASE}/{test_user.id}")).status_code == 401

    async def test_jwt_not_accepted_401(self, user_client, test_user):
        assert (await user_client.delete(f"{BASE}/{test_user.id}")).status_code == 401
