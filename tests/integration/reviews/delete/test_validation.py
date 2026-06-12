import pytest

from tests.integration.builders import INVALID_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/reviews"


class TestReviewsDeleteValidation:
    async def test_invalid_uuid_422(self, user_client):
        assert (await user_client.delete(f"{BASE}/{INVALID_UUID}")).status_code == 422
