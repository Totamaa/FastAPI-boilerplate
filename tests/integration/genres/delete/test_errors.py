import pytest

from tests.integration.builders import NONEXISTENT_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/genres"


class TestGenresDeleteErrors:
    async def test_not_found_404(self, admin_client):
        assert (await admin_client.delete(f"{BASE}/{NONEXISTENT_UUID}")).status_code == 404
