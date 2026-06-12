import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/genres"


class TestGenresGetAuth:
    async def test_public_no_auth(self, client, test_genre):
        assert (await client.get(f"{BASE}/{test_genre.id}")).status_code == 200
