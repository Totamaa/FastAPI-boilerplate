import pytest

from tests.integration.builders import NONEXISTENT_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/movie-cast"


class TestMovieCastListErrors:
    async def test_nonexistent_movie_returns_empty(self, client):
        r = await client.get(BASE, params={"movie_id": NONEXISTENT_UUID})
        assert r.status_code == 200 and r.json() == []
