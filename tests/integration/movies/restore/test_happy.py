import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesRestoreHappy:
    async def test_restore_returns_200(self, admin_client, test_movie):
        await admin_client.delete(f"{BASE}/{test_movie.id}")
        r = await admin_client.post(f"{BASE}/{test_movie.id}/restore")
        assert r.status_code == 200

    async def test_restored_movie_accessible(self, admin_client, client, test_movie):
        await admin_client.delete(f"{BASE}/{test_movie.id}")
        await admin_client.post(f"{BASE}/{test_movie.id}/restore")
        assert (await client.get(f"{BASE}/{test_movie.id}")).status_code == 200

    async def test_restored_movie_has_correct_data(self, admin_client, test_movie):
        await admin_client.delete(f"{BASE}/{test_movie.id}")
        r = await admin_client.post(f"{BASE}/{test_movie.id}/restore")
        data = r.json()
        assert data["id"] == str(test_movie.id)
        assert data["title"] == test_movie.title
