import pytest
from faker import Faker

from tests.integration.builders import director_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"
fake = Faker()


class TestDirectorsCreateErrors:
    async def test_two_directors_same_name_allowed(self, admin_client):
        name = fake.name()
        await admin_client.post(BASE, json=director_payload(full_name=name))
        assert (
            await admin_client.post(BASE, json=director_payload(full_name=name))
        ).status_code == 201
