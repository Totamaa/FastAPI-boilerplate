import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesListValidation:
    async def test_limit_below_1_returns_422(self, client):
        assert (await client.get(BASE, params={"limit": 0})).status_code == 422

    async def test_limit_above_100_returns_422(self, client):
        assert (await client.get(BASE, params={"limit": 101})).status_code == 422

    async def test_offset_negative_returns_422(self, client):
        assert (await client.get(BASE, params={"offset": -1})).status_code == 422

    async def test_invalid_limit_type_returns_422(self, client):
        assert (await client.get(BASE, params={"limit": "abc"})).status_code == 422

    async def test_invalid_status_value_returns_422(self, client):
        assert (await client.get(BASE, params={"status": "invalid_status"})).status_code == 422
