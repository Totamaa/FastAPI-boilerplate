import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"


class TestActorsListAuth:
    async def test_public_no_auth(self, client):
        assert (await client.get(BASE)).status_code == 200

    async def test_also_works_with_api_key(self, admin_client):
        assert (await admin_client.get(BASE)).status_code == 200
