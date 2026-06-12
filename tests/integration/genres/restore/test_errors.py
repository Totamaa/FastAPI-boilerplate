import pytest

from tests.integration.builders import NONEXISTENT_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/genres"


class TestGenresRestoreErrors:
    async def test_not_found_404(self, admin_client):
        assert (await admin_client.post(f"{BASE}/{NONEXISTENT_UUID}/restore")).status_code == 404
