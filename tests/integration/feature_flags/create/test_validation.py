import pytest

from tests.integration.builders import feature_flag_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/feature-flags"


class TestFeatureFlagsCreateValidation:
    async def test_missing_key_returns_422(self, admin_client):
        p = feature_flag_payload()
        del p["key"]
        assert (await admin_client.post(BASE, json=p)).status_code == 422

    async def test_key_with_uppercase_returns_422(self, admin_client):
        p = feature_flag_payload(key="Test:Flag")
        assert (await admin_client.post(BASE, json=p)).status_code == 422

    async def test_key_with_spaces_returns_422(self, admin_client):
        p = feature_flag_payload(key="test flag")
        assert (await admin_client.post(BASE, json=p)).status_code == 422

    async def test_rollout_over_100_returns_422(self, admin_client):
        p = feature_flag_payload(rollout_percentage=101)
        assert (await admin_client.post(BASE, json=p)).status_code == 422

    async def test_rollout_negative_returns_422(self, admin_client):
        p = feature_flag_payload(rollout_percentage=-1)
        assert (await admin_client.post(BASE, json=p)).status_code == 422

    async def test_invalid_uuid_in_allowed_user_ids_returns_422(self, admin_client):
        p = feature_flag_payload(allowed_user_ids=["not-a-uuid"])
        assert (await admin_client.post(BASE, json=p)).status_code == 422
