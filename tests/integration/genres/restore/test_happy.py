import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/genres"


class TestGenresRestoreHappy:
    async def test_restore_returns_200(self, admin_client, test_genre):
        await admin_client.delete(f"{BASE}/{test_genre.id}")
        r = await admin_client.post(f"{BASE}/{test_genre.id}/restore")
        assert r.status_code == 200

    async def test_restored_genre_accessible(self, admin_client, client, test_genre):
        await admin_client.delete(f"{BASE}/{test_genre.id}")
        await admin_client.post(f"{BASE}/{test_genre.id}/restore")
        assert (await client.get(f"{BASE}/{test_genre.id}")).status_code == 200

    async def test_restored_genre_has_correct_data(self, admin_client, test_genre):
        await admin_client.delete(f"{BASE}/{test_genre.id}")
        r = await admin_client.post(f"{BASE}/{test_genre.id}/restore")
        data = r.json()
        assert data["id"] == str(test_genre.id)
        assert data["name"] == test_genre.name
