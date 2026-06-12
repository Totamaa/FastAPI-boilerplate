import pytest

from tests.integration.builders import NONEXISTENT_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/reviews"


class TestReviewsDeleteErrors:
    async def test_not_found_404(self, user_client):
        assert (await user_client.delete(f"{BASE}/{NONEXISTENT_UUID}")).status_code == 404
