import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"


class TestDirectorsDeleteHappy:
    async def test_delete_returns_204(self, admin_client, test_director):
        assert (await admin_client.delete(f"{BASE}/{test_director.id}")).status_code == 204

    async def test_not_accessible_after_delete(self, admin_client, client, test_director):
        await admin_client.delete(f"{BASE}/{test_director.id}")
        assert (await client.get(f"{BASE}/{test_director.id}")).status_code == 404
