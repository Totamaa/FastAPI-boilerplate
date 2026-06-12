import pytest

from tests.factories import ActorFactory, MovieCastFactory, MovieFactory

pytestmark = pytest.mark.integration
BASE = "/api/v1/movie-cast"


class TestMovieCastListHappy:
    async def test_empty_list_200(self, client, test_movie):
        r = await client.get(BASE, params={"movie_id": str(test_movie.id)})
        assert r.status_code == 200 and r.json() == []

    async def test_returns_entries(self, client, test_cast_entry, test_movie):
        r = await client.get(BASE, params={"movie_id": str(test_movie.id)})
        assert r.status_code == 200 and len(r.json()) >= 1

    async def test_only_returns_movie_cast(
        self, client, db_session, test_cast_entry, test_movie, test_actor
    ):
        other_movie = await MovieFactory.create(db_session)
        other_actor = await ActorFactory.create(db_session)
        await MovieCastFactory.create(db_session, movie_id=other_movie.id, actor_id=other_actor.id)
        r = await client.get(BASE, params={"movie_id": str(test_movie.id)})
        assert all(e["movie_id"] == str(test_movie.id) for e in r.json())

    async def test_limit_respected(self, client, db_session, test_movie):
        actors = [await ActorFactory.create(db_session) for _ in range(3)]
        for a in actors:
            await MovieCastFactory.create(db_session, movie_id=test_movie.id, actor_id=a.id)
        r = await client.get(BASE, params={"movie_id": str(test_movie.id), "limit": 1})
        assert len(r.json()) == 1

    async def test_includes_actor_info(self, client, test_cast_entry, test_movie):
        r = await client.get(BASE, params={"movie_id": str(test_movie.id)})
        entry = r.json()[0]
        assert "actor_id" in entry or "actor" in entry
