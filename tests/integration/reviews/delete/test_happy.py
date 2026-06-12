import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/reviews"


class TestReviewsDeleteHappy:
    async def test_delete_returns_204(self, user_client, test_review):
        assert (await user_client.delete(f"{BASE}/{test_review.id}")).status_code == 204

    async def test_not_accessible_after_delete(self, user_client, client, test_review, test_movie):
        await user_client.delete(f"{BASE}/{test_review.id}")
        r = await client.get(BASE, params={"movie_id": str(test_movie.id)})
        ids = [rv["id"] for rv in r.json()]
        assert str(test_review.id) not in ids
