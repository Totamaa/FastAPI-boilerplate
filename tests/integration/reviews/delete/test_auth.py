import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/reviews"


class TestReviewsDeleteAuth:
    async def test_no_auth_401(self, client, test_review):
        assert (await client.delete(f"{BASE}/{test_review.id}")).status_code == 401

    async def test_other_user_forbidden_403(self, second_user_client, test_review):
        assert (await second_user_client.delete(f"{BASE}/{test_review.id}")).status_code == 403
