import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/feature-flags"


class TestFeatureFlagsUpdateErrors:
    async def test_nonexistent_key_returns_404(self, admin_client):
        r = await admin_client.patch(f"{BASE}/nonexistent:flag", json={"enabled": False})
        assert r.status_code == 404
