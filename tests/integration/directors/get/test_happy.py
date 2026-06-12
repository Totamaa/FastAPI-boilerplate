import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"


class TestDirectorsGetHappy:
    async def test_returns_200(self, client, test_director):
        assert (await client.get(f"{BASE}/{test_director.id}")).status_code == 200

    async def test_response_has_expected_fields(self, client, test_director):
        r = await client.get(f"{BASE}/{test_director.id}")
        d = r.json()
        assert d["id"] == str(test_director.id) and d["full_name"] == test_director.full_name
