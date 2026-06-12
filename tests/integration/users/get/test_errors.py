import pytest

from tests.integration.builders import NONEXISTENT_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/users"


class TestUsersGetErrors:
    async def test_not_found_404(self, admin_client):
        assert (await admin_client.get(f"{BASE}/{NONEXISTENT_UUID}")).status_code == 404
