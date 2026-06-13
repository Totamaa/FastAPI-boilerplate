import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/feature-flags"


class TestFeatureFlagsDeleteErrors:
    async def test_nonexistent_key_returns_404(self, admin_client):
        r = await admin_client.delete(f"{BASE}/nonexistent:flag")
        assert r.status_code == 404
