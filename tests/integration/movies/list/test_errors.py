import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesListErrors:
    async def test_status_filter_with_no_match_returns_empty_list(self, client):
        r = await client.get(BASE, params={"status": "upcoming"})
        assert r.status_code == 200 and r.json() == []
