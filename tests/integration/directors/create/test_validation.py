import pytest

from tests.integration.builders import director_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"


class TestDirectorsCreateValidation:
    async def test_missing_full_name_422(self, admin_client):
        p = {k: v for k, v in director_payload().items() if k != "full_name"}
        assert (await admin_client.post(BASE, json=p)).status_code == 422

    async def test_empty_full_name_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=director_payload(full_name=""))
        ).status_code == 422

    async def test_full_name_too_long_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=director_payload(full_name="a" * 256))
        ).status_code == 422

    async def test_nationality_too_long_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=director_payload(nationality="x" * 101))
        ).status_code == 422

    async def test_invalid_birth_date_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=director_payload(birth_date="bad"))
        ).status_code == 422

    async def test_empty_body_422(self, admin_client):
        assert (await admin_client.post(BASE, json={})).status_code == 422
