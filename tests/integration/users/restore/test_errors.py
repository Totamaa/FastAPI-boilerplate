import pytest

from tests.integration.builders import NONEXISTENT_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/users"


class TestUsersRestoreErrors:
    async def test_not_found_404(self, admin_client):
        assert (await admin_client.post(f"{BASE}/{NONEXISTENT_UUID}/restore")).status_code == 404
