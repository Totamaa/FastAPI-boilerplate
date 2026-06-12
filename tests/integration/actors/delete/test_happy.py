import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"


class TestActorsDeleteHappy:
    async def test_delete_returns_204(self, admin_client, test_actor):
        assert (await admin_client.delete(f"{BASE}/{test_actor.id}")).status_code == 204

    async def test_actor_not_accessible_after_delete(self, admin_client, client, test_actor):
        await admin_client.delete(f"{BASE}/{test_actor.id}")
        assert (await client.get(f"{BASE}/{test_actor.id}")).status_code == 404
