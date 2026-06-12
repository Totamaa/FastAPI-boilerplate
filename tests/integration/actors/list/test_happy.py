import pytest

from tests.factories import ActorFactory

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"


class TestActorsListHappy:
    async def test_empty_list_200(self, client):
        r = await client.get(BASE)
        assert r.status_code == 200 and r.json() == []

    async def test_returns_actors(self, client, db_session):
        await ActorFactory.create(db_session)
        await ActorFactory.create(db_session)
        r = await client.get(BASE)
        assert len(r.json()) == 2

    async def test_limit_respected(self, client, db_session):
        for _ in range(5):
            await ActorFactory.create(db_session)
        r = await client.get(BASE, params={"limit": 2})
        assert len(r.json()) == 2

    async def test_offset_skips_records(self, client, db_session):
        for _ in range(4):
            await ActorFactory.create(db_session)
        p1 = {a["id"] for a in (await client.get(BASE, params={"limit": 2, "offset": 0})).json()}
        p2 = {a["id"] for a in (await client.get(BASE, params={"limit": 2, "offset": 2})).json()}
        assert p1.isdisjoint(p2)
