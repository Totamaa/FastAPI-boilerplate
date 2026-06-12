import pytest

from tests.integration.builders import INVALID_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesDeleteValidation:
    async def test_invalid_uuid_format_422(self, admin_client):
        assert (await admin_client.delete(f"{BASE}/{INVALID_UUID}")).status_code == 422
