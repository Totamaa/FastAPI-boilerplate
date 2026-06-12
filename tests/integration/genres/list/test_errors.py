import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/genres"


class TestGenresListErrors:
    async def test_large_offset_empty_list(self, client):
        r = await client.get(BASE, params={"offset": 9999})
        assert r.status_code == 200 and r.json() == []
