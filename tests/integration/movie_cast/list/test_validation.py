import pytest

from tests.integration.builders import INVALID_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/movie-cast"


class TestMovieCastListValidation:
    async def test_missing_movie_id_422(self, client):
        assert (await client.get(BASE)).status_code == 422

    async def test_invalid_movie_id_422(self, client):
        assert (await client.get(BASE, params={"movie_id": INVALID_UUID})).status_code == 422

    async def test_limit_below_1_422(self, client, test_movie):
        assert (
            await client.get(BASE, params={"movie_id": str(test_movie.id), "limit": 0})
        ).status_code == 422

    async def test_offset_negative_422(self, client, test_movie):
        assert (
            await client.get(BASE, params={"movie_id": str(test_movie.id), "offset": -1})
        ).status_code == 422
