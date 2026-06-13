import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/feature-flags"


class TestFeatureFlagsUpdateValidation:
    async def test_rollout_over_100_returns_422(self, admin_client, test_flag):
        r = await admin_client.patch(f"{BASE}/{test_flag.key}", json={"rollout_percentage": 101})
        assert r.status_code == 422

    async def test_rollout_negative_returns_422(self, admin_client, test_flag):
        r = await admin_client.patch(f"{BASE}/{test_flag.key}", json={"rollout_percentage": -1})
        assert r.status_code == 422
