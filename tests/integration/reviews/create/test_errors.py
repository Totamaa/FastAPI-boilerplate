import pytest

from tests.integration.builders import NONEXISTENT_UUID, review_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/reviews"


class TestReviewsCreateErrors:
    async def test_movie_not_found_404(self, user_client):
        r = await user_client.post(BASE, json=review_payload(NONEXISTENT_UUID))
        assert r.status_code == 404

    async def test_duplicate_review_409(self, user_client, test_movie, test_review):
        r = await user_client.post(BASE, json=review_payload(str(test_movie.id)))
        assert r.status_code == 409
