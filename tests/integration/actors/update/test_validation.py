import pytest

from tests.integration.builders import INVALID_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"


class TestActorsUpdateValidation:
    async def test_empty_full_name_422(self, admin_client, test_actor):
        assert (
            await admin_client.put(f"{BASE}/{test_actor.id}", json={"full_name": ""})
        ).status_code == 422

    async def test_full_name_too_long_422(self, admin_client, test_actor):
        assert (
            await admin_client.put(f"{BASE}/{test_actor.id}", json={"full_name": "a" * 256})
        ).status_code == 422

    async def test_nationality_too_long_422(self, admin_client, test_actor):
        assert (
            await admin_client.put(f"{BASE}/{test_actor.id}", json={"nationality": "x" * 101})
        ).status_code == 422

    async def test_invalid_birth_date_422(self, admin_client, test_actor):
        assert (
            await admin_client.put(f"{BASE}/{test_actor.id}", json={"birth_date": "bad-date"})
        ).status_code == 422

    async def test_invalid_uuid_format_422(self, admin_client):
        assert (
            await admin_client.put(f"{BASE}/{INVALID_UUID}", json={"full_name": "x"})
        ).status_code == 422
