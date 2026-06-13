import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/feature-flags"


class TestFeatureFlagsUpdateAuth:
    async def test_no_api_key_returns_401(self, client, test_flag):
        r = await client.patch(f"{BASE}/{test_flag.key}", json={"enabled": False})
        assert r.status_code == 401

    async def test_jwt_not_accepted(self, user_client, test_flag):
        r = await user_client.patch(f"{BASE}/{test_flag.key}", json={"enabled": False})
        assert r.status_code == 401
