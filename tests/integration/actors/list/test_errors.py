import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"


class TestActorsListErrors:
    async def test_large_offset_returns_empty_not_error(self, client):
        r = await client.get(BASE, params={"offset": 9999})
        assert r.status_code == 200 and r.json() == []
