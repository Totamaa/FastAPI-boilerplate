import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/genres"


class TestGenresListAuth:
    async def test_public_no_auth(self, client):
        assert (await client.get(BASE)).status_code == 200
