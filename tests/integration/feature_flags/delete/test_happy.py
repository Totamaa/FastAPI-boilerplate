import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/feature-flags"


class TestFeatureFlagsDeleteHappy:
    async def test_delete_returns_204(self, admin_client, test_flag):
        r = await admin_client.delete(f"{BASE}/{test_flag.key}")
        assert r.status_code == 204

    async def test_deleted_flag_not_in_list(self, admin_client, test_flag):
        await admin_client.delete(f"{BASE}/{test_flag.key}")
        keys = [f["key"] for f in (await admin_client.get(BASE)).json()]
        assert test_flag.key not in keys
