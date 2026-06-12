import pytest

from tests.integration.builders import NONEXISTENT_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/movie-cast"


class TestMovieCastUpdateErrors:
    async def test_not_found_404(self, admin_client):
        assert (
            await admin_client.put(f"{BASE}/{NONEXISTENT_UUID}", json={"billing_order": 2})
        ).status_code == 404
