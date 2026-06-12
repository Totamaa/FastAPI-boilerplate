import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"


class TestActorsGetAuth:
    async def test_public_no_auth(self, client, test_actor):
        assert (await client.get(f"{BASE}/{test_actor.id}")).status_code == 200

    async def test_also_works_with_api_key(self, admin_client, test_actor):
        assert (await admin_client.get(f"{BASE}/{test_actor.id}")).status_code == 200
