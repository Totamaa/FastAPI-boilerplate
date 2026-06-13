import pytest

from tests.integration.builders import feature_flag_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/feature-flags"


class TestFeatureFlagsListHappy:
    async def test_returns_200(self, admin_client):
        r = await admin_client.get(BASE)
        assert r.status_code == 200

    async def test_returns_list(self, admin_client):
        r = await admin_client.get(BASE)
        assert isinstance(r.json(), list)

    async def test_created_flag_appears_in_list(self, admin_client, db_session):
        p = feature_flag_payload()
        await admin_client.post(BASE, json=p)
        keys = [f["key"] for f in (await admin_client.get(BASE)).json()]
        assert p["key"] in keys

    async def test_response_schema(self, admin_client):
        p = feature_flag_payload()
        await admin_client.post(BASE, json=p)
        flags = (await admin_client.get(BASE)).json()
        matching = [f for f in flags if f["key"] == p["key"]]
        assert len(matching) == 1
        flag = matching[0]
        assert all(
            k in flag
            for k in ("key", "enabled", "rollout_percentage", "allowed_user_ids", "updated_at")
        )
