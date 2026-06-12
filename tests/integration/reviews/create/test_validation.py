import pytest

from tests.integration.builders import review_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/reviews"


class TestReviewsCreateValidation:
    async def test_missing_movie_id_422(self, user_client, test_movie):
        p = {k: v for k, v in review_payload(str(test_movie.id)).items() if k != "movie_id"}
        assert (await user_client.post(BASE, json=p)).status_code == 422

    async def test_missing_rating_422(self, user_client, test_movie):
        p = {k: v for k, v in review_payload(str(test_movie.id)).items() if k != "rating"}
        assert (await user_client.post(BASE, json=p)).status_code == 422

    async def test_rating_below_1_422(self, user_client, test_movie):
        assert (
            await user_client.post(BASE, json=review_payload(str(test_movie.id), rating=0))
        ).status_code == 422

    async def test_rating_above_10_422(self, user_client, test_movie):
        assert (
            await user_client.post(BASE, json=review_payload(str(test_movie.id), rating=11))
        ).status_code == 422

    async def test_rating_float_422(self, user_client, test_movie):
        assert (
            await user_client.post(BASE, json=review_payload(str(test_movie.id), rating=4.5))
        ).status_code == 422

    async def test_invalid_movie_id_422(self, user_client):
        from tests.integration.builders import INVALID_UUID

        assert (await user_client.post(BASE, json=review_payload(INVALID_UUID))).status_code == 422

    async def test_empty_body_422(self, user_client):
        assert (await user_client.post(BASE, json={})).status_code == 422
