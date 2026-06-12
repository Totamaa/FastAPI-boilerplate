import pytest

from tests.factories import DirectorFactory

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"


class TestDirectorsListHappy:
    async def test_empty_list_200(self, client):
        r = await client.get(BASE)
        assert r.status_code == 200 and r.json() == []

    async def test_returns_directors(self, client, db_session):
        await DirectorFactory.create(db_session)
        await DirectorFactory.create(db_session)
        assert len((await client.get(BASE)).json()) == 2

    async def test_limit_respected(self, client, db_session):
        for _ in range(5):
            await DirectorFactory.create(db_session)
        assert len((await client.get(BASE, params={"limit": 2})).json()) == 2

    async def test_offset_skips_records(self, client, db_session):
        for _ in range(4):
            await DirectorFactory.create(db_session)
        p1 = {d["id"] for d in (await client.get(BASE, params={"limit": 2, "offset": 0})).json()}
        p2 = {d["id"] for d in (await client.get(BASE, params={"limit": 2, "offset": 2})).json()}
        assert p1.isdisjoint(p2)
