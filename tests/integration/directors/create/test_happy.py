import pytest
from faker import Faker

from tests.integration.builders import director_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"
fake = Faker()


class TestDirectorsCreateHappy:
    async def test_minimal_payload_201(self, admin_client):
        r = await admin_client.post(BASE, json=director_payload())
        assert r.status_code == 201

    async def test_response_has_expected_fields(self, admin_client):
        p = director_payload()
        r = await admin_client.post(BASE, json=p)
        d = r.json()
        assert d["full_name"] == p["full_name"] and "id" in d

    async def test_create_with_optional_fields(self, admin_client):
        r = await admin_client.post(
            BASE,
            json=director_payload(
                birth_date=str(fake.date_of_birth(minimum_age=30, maximum_age=80)),
                nationality=fake.country()[:100],
                biography=fake.paragraph(),
            ),
        )
        assert r.status_code == 201

    async def test_extra_fields_ignored(self, admin_client):
        assert (await admin_client.post(BASE, json=director_payload(extra="x"))).status_code == 201
