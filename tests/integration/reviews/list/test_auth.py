import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/reviews"


class TestReviewsListAuth:
    async def test_public_no_auth(self, client, test_movie):
        assert (await client.get(BASE, params={"movie_id": str(test_movie.id)})).status_code == 200
