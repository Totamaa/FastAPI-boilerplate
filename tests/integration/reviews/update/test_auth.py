import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/reviews"


class TestReviewsUpdateAuth:
    async def test_no_auth_401(self, client, test_review):
        assert (await client.put(f"{BASE}/{test_review.id}", json={"rating": 7})).status_code == 401

    async def test_api_key_not_accepted_401(self, admin_client, test_review):
        assert (
            await admin_client.put(f"{BASE}/{test_review.id}", json={"rating": 7})
        ).status_code == 401

    async def test_other_user_forbidden_403(self, second_user_client, test_review):
        assert (
            await second_user_client.put(f"{BASE}/{test_review.id}", json={"rating": 7})
        ).status_code == 403
