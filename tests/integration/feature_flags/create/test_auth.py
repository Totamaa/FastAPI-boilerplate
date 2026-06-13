import pytest

from tests.integration.builders import feature_flag_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/feature-flags"


class TestFeatureFlagsCreateAuth:
    async def test_no_api_key_returns_401(self, client):
        assert (await client.post(BASE, json=feature_flag_payload())).status_code == 401

    async def test_wrong_key_returns_401(self, client):
        r = await client.post(BASE, json=feature_flag_payload(), headers={"X-API-Key": "bad"})
        assert r.status_code == 401

    async def test_jwt_not_accepted(self, user_client):
        assert (await user_client.post(BASE, json=feature_flag_payload())).status_code == 401
