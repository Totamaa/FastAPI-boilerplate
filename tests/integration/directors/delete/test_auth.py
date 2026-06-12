import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"


class TestDirectorsDeleteAuth:
    async def test_no_api_key_401(self, client, test_director):
        assert (await client.delete(f"{BASE}/{test_director.id}")).status_code == 401

    async def test_jwt_not_accepted_401(self, user_client, test_director):
        assert (await user_client.delete(f"{BASE}/{test_director.id}")).status_code == 401
