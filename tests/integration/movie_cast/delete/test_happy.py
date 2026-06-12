import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/movie-cast"


class TestMovieCastDeleteHappy:
    async def test_delete_returns_204(self, admin_client, test_cast_entry):
        assert (await admin_client.delete(f"{BASE}/{test_cast_entry.id}")).status_code == 204

    async def test_not_accessible_after_delete(
        self, admin_client, client, test_cast_entry, test_movie
    ):
        entry_id = str(test_cast_entry.id)
        await admin_client.delete(f"{BASE}/{test_cast_entry.id}")
        r = await client.get(BASE, params={"movie_id": str(test_movie.id)})
        ids = [e["id"] for e in r.json()]
        assert entry_id not in ids
