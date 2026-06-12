import pytest

from tests.integration.builders import INVALID_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/reviews"


class TestReviewsUpdateValidation:
    async def test_invalid_uuid_422(self, user_client):
        assert (
            await user_client.put(f"{BASE}/{INVALID_UUID}", json={"rating": 5})
        ).status_code == 422

    async def test_rating_below_1_422(self, user_client, test_review):
        assert (
            await user_client.put(f"{BASE}/{test_review.id}", json={"rating": 0})
        ).status_code == 422

    async def test_rating_above_10_422(self, user_client, test_review):
        assert (
            await user_client.put(f"{BASE}/{test_review.id}", json={"rating": 11})
        ).status_code == 422
