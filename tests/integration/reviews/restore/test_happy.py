import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/reviews"


class TestReviewsRestoreHappy:
    async def test_restore_returns_200(self, admin_client, user_client, test_review):
        await user_client.delete(f"{BASE}/{test_review.id}")
        r = await admin_client.post(f"{BASE}/{test_review.id}/restore")
        assert r.status_code == 200

    async def test_restored_review_appears_in_listing(
        self, admin_client, user_client, client, test_movie, test_review
    ):
        await user_client.delete(f"{BASE}/{test_review.id}")
        await admin_client.post(f"{BASE}/{test_review.id}/restore")
        r = await client.get(BASE, params={"movie_id": str(test_movie.id)})
        ids = [item["id"] for item in r.json()]
        assert str(test_review.id) in ids

    async def test_restored_review_has_correct_data(self, admin_client, user_client, test_review):
        await user_client.delete(f"{BASE}/{test_review.id}")
        r = await admin_client.post(f"{BASE}/{test_review.id}/restore")
        data = r.json()
        assert data["id"] == str(test_review.id)
        assert data["movie_id"] == str(test_review.movie_id)
