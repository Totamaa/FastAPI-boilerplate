import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/feature-flags"


class TestFeatureFlagsListAuth:
    async def test_no_api_key_returns_401(self, client):
        assert (await client.get(BASE)).status_code == 401

    async def test_wrong_key_returns_401(self, client):
        assert (await client.get(BASE, headers={"X-API-Key": "bad"})).status_code == 401

    async def test_jwt_not_accepted(self, user_client):
        assert (await user_client.get(BASE)).status_code == 401
