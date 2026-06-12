import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"


class TestActorsListValidation:
    async def test_limit_below_1_422(self, client):
        assert (await client.get(BASE, params={"limit": 0})).status_code == 422

    async def test_limit_above_100_422(self, client):
        assert (await client.get(BASE, params={"limit": 101})).status_code == 422

    async def test_offset_negative_422(self, client):
        assert (await client.get(BASE, params={"offset": -1})).status_code == 422

    async def test_invalid_limit_type_422(self, client):
        assert (await client.get(BASE, params={"limit": "bad"})).status_code == 422
