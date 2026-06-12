import pytest

from tests.factories import MovieFactory

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"


class TestDirectorsMoviesHappy:
    async def test_empty_list_when_no_movies(self, client, test_director):
        r = await client.get(f"{BASE}/{test_director.id}/movies")
        assert r.status_code == 200 and r.json() == []

    async def test_returns_director_movies(self, client, db_session, test_director):
        await MovieFactory.create(db_session, director_id=test_director.id)
        await MovieFactory.create(db_session, director_id=test_director.id)
        r = await client.get(f"{BASE}/{test_director.id}/movies")
        assert r.status_code == 200 and len(r.json()) == 2

    async def test_does_not_return_other_directors_movies(self, client, db_session, test_director):
        from tests.factories import DirectorFactory

        other = await DirectorFactory.create(db_session)
        await MovieFactory.create(db_session, director_id=other.id)
        r = await client.get(f"{BASE}/{test_director.id}/movies")
        assert r.json() == []

    async def test_limit_respected(self, client, db_session, test_director):
        for _ in range(5):
            await MovieFactory.create(db_session, director_id=test_director.id)
        r = await client.get(f"{BASE}/{test_director.id}/movies", params={"limit": 2})
        assert len(r.json()) == 2
