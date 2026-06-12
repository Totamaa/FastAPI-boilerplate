import pytest

from tests.factories import MovieCastFactory, MovieFactory

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"


class TestActorsGetHappy:
    async def test_returns_200(self, client, test_actor):
        assert (await client.get(f"{BASE}/{test_actor.id}")).status_code == 200

    async def test_response_has_expected_fields(self, client, test_actor):
        r = await client.get(f"{BASE}/{test_actor.id}")
        d = r.json()
        assert d["id"] == str(test_actor.id)
        assert d["full_name"] == test_actor.full_name

    async def test_filmography_null_by_default(self, client, test_actor):
        r = await client.get(f"{BASE}/{test_actor.id}")
        assert r.json()["filmography"] is None

    async def test_filmography_populated_with_include_movies(self, client, db_session, test_actor):
        movie = await MovieFactory.create(db_session)
        await MovieCastFactory.create(db_session, movie_id=movie.id, actor_id=test_actor.id)
        r = await client.get(f"{BASE}/{test_actor.id}", params={"include": "movies"})
        assert r.json()["filmography"] is not None and len(r.json()["filmography"]) == 1
