import pytest
from faker import Faker

from tests.integration.builders import actor_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"
fake = Faker()


class TestActorsCreateValidation:
    async def test_missing_full_name_422(self, admin_client):
        p = {k: v for k, v in actor_payload().items() if k != "full_name"}
        assert (await admin_client.post(BASE, json=p)).status_code == 422

    async def test_empty_full_name_422(self, admin_client):
        assert (await admin_client.post(BASE, json=actor_payload(full_name=""))).status_code == 422

    async def test_full_name_too_long_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=actor_payload(full_name="a" * 256))
        ).status_code == 422

    async def test_nationality_too_long_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=actor_payload(nationality="x" * 101))
        ).status_code == 422

    async def test_invalid_birth_date_format_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=actor_payload(birth_date="not-a-date"))
        ).status_code == 422

    async def test_empty_body_422(self, admin_client):
        assert (await admin_client.post(BASE, json={})).status_code == 422
