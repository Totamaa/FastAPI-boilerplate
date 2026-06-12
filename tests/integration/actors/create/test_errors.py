import pytest
from faker import Faker

from tests.integration.builders import actor_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"
fake = Faker()


class TestActorsCreateErrors:
    async def test_two_actors_same_name_is_allowed(self, admin_client):
        name = fake.name()
        await admin_client.post(BASE, json=actor_payload(full_name=name))
        r = await admin_client.post(BASE, json=actor_payload(full_name=name))
        assert r.status_code == 201
