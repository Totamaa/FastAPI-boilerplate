import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesDeleteHappy:
    async def test_delete_returns_204(self, admin_client, test_movie):
        assert (await admin_client.delete(f"{BASE}/{test_movie.id}")).status_code == 204

    async def test_movie_no_longer_accessible_after_delete(self, admin_client, client, test_movie):
        await admin_client.delete(f"{BASE}/{test_movie.id}")
        assert (await client.get(f"{BASE}/{test_movie.id}")).status_code == 404
