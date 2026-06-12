import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/genres"


class TestGenresDeleteHappy:
    async def test_delete_returns_204(self, admin_client, test_genre):
        assert (await admin_client.delete(f"{BASE}/{test_genre.id}")).status_code == 204

    async def test_not_accessible_after_delete(self, admin_client, client, test_genre):
        await admin_client.delete(f"{BASE}/{test_genre.id}")
        assert (await client.get(f"{BASE}/{test_genre.id}")).status_code == 404
