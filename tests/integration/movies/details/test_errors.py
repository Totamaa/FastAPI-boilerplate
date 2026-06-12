import pytest

from tests.integration.builders import NONEXISTENT_UUID

pytestmark = pytest.mark.integration


class TestMoviesDetailsErrors:
    async def test_nonexistent_movie_404(self, admin_client):
        r = await admin_client.patch(f"/api/v1/movies/{NONEXISTENT_UUID}/details", json={})
        assert r.status_code == 404
