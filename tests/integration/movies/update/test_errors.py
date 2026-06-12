import pytest

from tests.integration.builders import NONEXISTENT_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesUpdateErrors:
    async def test_not_found_404(self, admin_client):
        assert (
            await admin_client.put(f"{BASE}/{NONEXISTENT_UUID}", json={"title": "x"})
        ).status_code == 404

    async def test_nonexistent_director_400(self, admin_client, test_movie):
        r = await admin_client.put(
            f"{BASE}/{test_movie.id}", json={"director_id": NONEXISTENT_UUID}
        )
        assert r.status_code in (400, 404)
