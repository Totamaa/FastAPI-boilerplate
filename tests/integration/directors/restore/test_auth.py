import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"


class TestDirectorsRestoreAuth:
    async def test_no_api_key_401(self, client, test_director):
        assert (await client.post(f"{BASE}/{test_director.id}/restore")).status_code == 401

    async def test_jwt_not_accepted_401(self, user_client, test_director):
        assert (await user_client.post(f"{BASE}/{test_director.id}/restore")).status_code == 401
