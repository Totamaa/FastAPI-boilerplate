import pytest

from tests.factories import GenreFactory

pytestmark = pytest.mark.integration
BASE = "/api/v1/genres"


class TestGenresListHappy:
    async def test_returns_200(self, client):
        r = await client.get(BASE)
        assert r.status_code == 200 and isinstance(r.json(), list)

    async def test_returns_genres(self, client, db_session):
        before = len((await client.get(BASE)).json())
        await GenreFactory.create(db_session)
        await GenreFactory.create(db_session)
        after = len((await client.get(BASE)).json())
        assert after == before + 2

    async def test_limit_respected(self, client, db_session):
        for _ in range(3):
            await GenreFactory.create(db_session)
        r = await client.get(BASE, params={"limit": 1})
        assert len(r.json()) == 1
