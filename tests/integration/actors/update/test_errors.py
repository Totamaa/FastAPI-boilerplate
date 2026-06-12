import pytest

from tests.integration.builders import NONEXISTENT_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"


class TestActorsUpdateErrors:
    async def test_not_found_404(self, admin_client):
        assert (
            await admin_client.put(f"{BASE}/{NONEXISTENT_UUID}", json={"full_name": "x"})
        ).status_code == 404
