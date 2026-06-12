import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/genres"


class TestGenresGetHappy:
    async def test_returns_200(self, client, test_genre):
        assert (await client.get(f"{BASE}/{test_genre.id}")).status_code == 200

    async def test_response_has_expected_fields(self, client, test_genre):
        r = await client.get(f"{BASE}/{test_genre.id}")
        d = r.json()
        assert d["id"] == str(test_genre.id) and d["name"] == test_genre.name
