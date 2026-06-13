import pytest

from tests.integration.builders import feature_flag_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/feature-flags"


class TestFeatureFlagsCreateHappy:
    async def test_creates_flag_201(self, admin_client):
        r = await admin_client.post(BASE, json=feature_flag_payload())
        assert r.status_code == 201

    async def test_response_has_expected_fields(self, admin_client):
        p = feature_flag_payload()
        d = (await admin_client.post(BASE, json=p)).json()
        assert d["key"] == p["key"]
        assert d["enabled"] == p["enabled"]
        assert d["rollout_percentage"] == p["rollout_percentage"]
        assert "updated_at" in d

    async def test_creates_disabled_flag(self, admin_client):
        p = feature_flag_payload(enabled=False, rollout_percentage=0)
        r = await admin_client.post(BASE, json=p)
        assert r.status_code == 201 and r.json()["enabled"] is False

    async def test_creates_flag_with_description(self, admin_client):
        p = feature_flag_payload(description="My feature description")
        r = await admin_client.post(BASE, json=p)
        assert r.status_code == 201 and r.json()["description"] == "My feature description"
