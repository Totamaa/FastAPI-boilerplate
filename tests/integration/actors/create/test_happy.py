import pytest
from faker import Faker

from tests.integration.builders import actor_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"
fake = Faker()


class TestActorsCreateHappy:
    async def test_minimal_payload_201(self, admin_client):
        r = await admin_client.post(BASE, json=actor_payload())
        assert r.status_code == 201

    async def test_response_has_expected_fields(self, admin_client):
        p = actor_payload()
        r = await admin_client.post(BASE, json=p)
        d = r.json()
        assert d["full_name"] == p["full_name"]
        assert "id" in d and "created_at" in d

    async def test_create_with_all_optional_fields(self, admin_client):
        r = await admin_client.post(
            BASE,
            json=actor_payload(
                birth_date=str(fake.date_of_birth(minimum_age=20, maximum_age=80)),
                nationality=fake.country()[:100],
                biography=fake.paragraph(),
            ),
        )
        assert r.status_code == 201

    async def test_extra_fields_ignored(self, admin_client):
        r = await admin_client.post(BASE, json=actor_payload(unknown="x"))
        assert r.status_code == 201
