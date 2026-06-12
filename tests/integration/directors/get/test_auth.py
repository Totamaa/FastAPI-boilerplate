import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"


class TestDirectorsGetAuth:
    async def test_public_no_auth(self, client, test_director):
        assert (await client.get(f"{BASE}/{test_director.id}")).status_code == 200
