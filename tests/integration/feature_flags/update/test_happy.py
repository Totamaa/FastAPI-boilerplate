import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/feature-flags"


class TestFeatureFlagsUpdateHappy:
    async def test_disable_flag(self, admin_client, test_flag):
        r = await admin_client.patch(f"{BASE}/{test_flag.key}", json={"enabled": False})
        assert r.status_code == 200 and r.json()["enabled"] is False

    async def test_change_rollout_percentage(self, admin_client, test_flag):
        r = await admin_client.patch(f"{BASE}/{test_flag.key}", json={"rollout_percentage": 75})
        assert r.status_code == 200 and r.json()["rollout_percentage"] == 75

    async def test_empty_patch_returns_200(self, admin_client, test_flag):
        r = await admin_client.patch(f"{BASE}/{test_flag.key}", json={})
        assert r.status_code == 200 and r.json()["key"] == test_flag.key

    async def test_update_description(self, admin_client, test_flag):
        r = await admin_client.patch(f"{BASE}/{test_flag.key}", json={"description": "updated"})
        assert r.status_code == 200 and r.json()["description"] == "updated"
