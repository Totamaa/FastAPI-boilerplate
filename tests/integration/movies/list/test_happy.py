import pytest

from tests.factories import MovieFactory

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesListHappy:
    async def test_empty_list_returns_200(self, client):
        r = await client.get(BASE)
        assert r.status_code == 200 and r.json() == []

    async def test_returns_created_movies(self, client, db_session):
        await MovieFactory.create(db_session)
        await MovieFactory.create(db_session)
        r = await client.get(BASE)
        assert r.status_code == 200 and len(r.json()) == 2

    async def test_limit_param_respected(self, client, db_session):
        for _ in range(5):
            await MovieFactory.create(db_session)
        r = await client.get(BASE, params={"limit": 2})
        assert r.status_code == 200 and len(r.json()) == 2

    async def test_offset_param_skips_records(self, client, db_session):
        for _ in range(4):
            await MovieFactory.create(db_session)
        page1 = (await client.get(BASE, params={"limit": 2, "offset": 0})).json()
        page2 = (await client.get(BASE, params={"limit": 2, "offset": 2})).json()
        ids1 = {m["id"] for m in page1}
        ids2 = {m["id"] for m in page2}
        assert ids1.isdisjoint(ids2)

    async def test_filter_by_status(self, client, db_session):
        await MovieFactory.create(db_session, status="released")
        await MovieFactory.create(db_session, status="upcoming")
        r = await client.get(BASE, params={"status": "upcoming"})
        data = r.json()
        assert all(m["status"] == "upcoming" for m in data)

    async def test_public_no_auth_needed(self, client, db_session):
        await MovieFactory.create(db_session)
        r = await client.get(BASE)
        assert r.status_code == 200
