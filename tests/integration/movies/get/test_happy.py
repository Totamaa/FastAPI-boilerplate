import pytest

from tests.factories import DirectorFactory

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesGetHappy:
    async def test_returns_200(self, client, test_movie):
        assert (await client.get(f"{BASE}/{test_movie.id}")).status_code == 200

    async def test_response_is_detailed(self, client, test_movie):
        r = await client.get(f"{BASE}/{test_movie.id}")
        d = r.json()
        assert d["id"] == str(test_movie.id)
        assert "genres" in d and "cast" in d

    async def test_includes_director_when_set(self, admin_client, db_session):
        from tests.integration.builders import movie_payload

        director = await DirectorFactory.create(db_session)
        r = await admin_client.post(BASE, json=movie_payload(director_id=str(director.id)))
        movie_id = r.json()["id"]
        detail = await admin_client.get(f"{BASE}/{movie_id}")
        assert detail.json()["director"]["id"] == str(director.id)

    async def test_includes_cast_entries(self, client, db_session, test_movie, test_cast_entry):
        r = await client.get(f"{BASE}/{test_movie.id}")
        cast = r.json()["cast"]
        assert len(cast) == 1
