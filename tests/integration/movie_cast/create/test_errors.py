import pytest

from tests.integration.builders import NONEXISTENT_UUID, cast_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/movie-cast"


class TestMovieCastCreateErrors:
    async def test_movie_not_found_404(self, admin_client, test_actor):
        r = await admin_client.post(BASE, json=cast_payload(NONEXISTENT_UUID, str(test_actor.id)))
        assert r.status_code == 404

    async def test_actor_not_found_404(self, admin_client, test_movie):
        r = await admin_client.post(BASE, json=cast_payload(str(test_movie.id), NONEXISTENT_UUID))
        assert r.status_code == 404

    async def test_duplicate_entry_409(self, admin_client, test_movie, test_actor, test_cast_entry):
        r = await admin_client.post(BASE, json=cast_payload(str(test_movie.id), str(test_actor.id)))
        assert r.status_code == 409
