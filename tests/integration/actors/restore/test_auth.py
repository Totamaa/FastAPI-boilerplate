import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"


class TestActorsRestoreAuth:
    async def test_no_api_key_401(self, client, test_actor):
        assert (await client.post(f"{BASE}/{test_actor.id}/restore")).status_code == 401

    async def test_jwt_not_accepted_401(self, user_client, test_actor):
        assert (await user_client.post(f"{BASE}/{test_actor.id}/restore")).status_code == 401
