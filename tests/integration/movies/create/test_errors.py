import pytest

from tests.integration.builders import NONEXISTENT_UUID, movie_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesCreateErrors:
    async def test_nonexistent_director_404(self, admin_client):
        r = await admin_client.post(BASE, json=movie_payload(director_id=NONEXISTENT_UUID))
        assert r.status_code == 404

    async def test_nonexistent_genre_404(self, admin_client):
        r = await admin_client.post(BASE, json=movie_payload(genre_ids=[NONEXISTENT_UUID]))
        assert r.status_code == 404
