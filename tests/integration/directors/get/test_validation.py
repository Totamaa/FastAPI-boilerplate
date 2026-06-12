import pytest

from tests.integration.builders import INVALID_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"


class TestDirectorsGetValidation:
    async def test_invalid_uuid_422(self, client):
        assert (await client.get(f"{BASE}/{INVALID_UUID}")).status_code == 422
