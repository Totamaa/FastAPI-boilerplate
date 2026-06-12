import pytest

from tests.integration.builders import INVALID_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesRestoreValidation:
    async def test_invalid_uuid_422(self, admin_client):
        assert (await admin_client.post(f"{BASE}/{INVALID_UUID}/restore")).status_code == 422
