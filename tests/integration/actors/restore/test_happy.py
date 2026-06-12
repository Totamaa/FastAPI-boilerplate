import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"


class TestActorsRestoreHappy:
    async def test_restore_returns_200(self, admin_client, test_actor):
        await admin_client.delete(f"{BASE}/{test_actor.id}")
        r = await admin_client.post(f"{BASE}/{test_actor.id}/restore")
        assert r.status_code == 200

    async def test_restored_actor_accessible(self, admin_client, client, test_actor):
        await admin_client.delete(f"{BASE}/{test_actor.id}")
        await admin_client.post(f"{BASE}/{test_actor.id}/restore")
        assert (await client.get(f"{BASE}/{test_actor.id}")).status_code == 200

    async def test_restored_actor_has_correct_data(self, admin_client, test_actor):
        await admin_client.delete(f"{BASE}/{test_actor.id}")
        r = await admin_client.post(f"{BASE}/{test_actor.id}/restore")
        data = r.json()
        assert data["id"] == str(test_actor.id)
        assert data["full_name"] == test_actor.full_name
