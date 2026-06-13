import pytest

from tests.integration.builders import feature_flag_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/feature-flags"


class TestFeatureFlagsCreateErrors:
    async def test_duplicate_key_returns_409(self, admin_client):
        p = feature_flag_payload()
        await admin_client.post(BASE, json=p)
        r = await admin_client.post(BASE, json=p)
        assert r.status_code == 409
