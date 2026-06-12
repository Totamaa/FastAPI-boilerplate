import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"


class TestDirectorsRestoreHappy:
    async def test_restore_returns_200(self, admin_client, test_director):
        await admin_client.delete(f"{BASE}/{test_director.id}")
        r = await admin_client.post(f"{BASE}/{test_director.id}/restore")
        assert r.status_code == 200

    async def test_restored_director_accessible(self, admin_client, client, test_director):
        await admin_client.delete(f"{BASE}/{test_director.id}")
        await admin_client.post(f"{BASE}/{test_director.id}/restore")
        assert (await client.get(f"{BASE}/{test_director.id}")).status_code == 200

    async def test_restored_director_has_correct_data(self, admin_client, test_director):
        await admin_client.delete(f"{BASE}/{test_director.id}")
        r = await admin_client.post(f"{BASE}/{test_director.id}/restore")
        data = r.json()
        assert data["id"] == str(test_director.id)
        assert data["full_name"] == test_director.full_name
