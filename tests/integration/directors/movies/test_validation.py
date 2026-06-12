import pytest

from tests.integration.builders import INVALID_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"


class TestDirectorsMoviesValidation:
    async def test_invalid_uuid_422(self, client):
        assert (await client.get(f"{BASE}/{INVALID_UUID}/movies")).status_code == 422

    async def test_limit_below_1_422(self, client, test_director):
        assert (
            await client.get(f"{BASE}/{test_director.id}/movies", params={"limit": 0})
        ).status_code == 422

    async def test_limit_above_100_422(self, client, test_director):
        assert (
            await client.get(f"{BASE}/{test_director.id}/movies", params={"limit": 101})
        ).status_code == 422
