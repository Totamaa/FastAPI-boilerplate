import pytest

from tests.integration.builders import INVALID_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/movie-cast"


class TestMovieCastUpdateValidation:
    async def test_invalid_uuid_422(self, admin_client):
        assert (
            await admin_client.put(f"{BASE}/{INVALID_UUID}", json={"billing_order": 2})
        ).status_code == 422

    async def test_billing_order_below_1_422(self, admin_client, test_cast_entry):
        assert (
            await admin_client.put(f"{BASE}/{test_cast_entry.id}", json={"billing_order": 0})
        ).status_code == 422

    async def test_empty_role_name_422(self, admin_client, test_cast_entry):
        assert (
            await admin_client.put(f"{BASE}/{test_cast_entry.id}", json={"role_name": ""})
        ).status_code == 422
