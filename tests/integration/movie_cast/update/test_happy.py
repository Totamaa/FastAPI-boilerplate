import pytest
from faker import Faker

pytestmark = pytest.mark.integration
BASE = "/api/v1/movie-cast"
fake = Faker()


class TestMovieCastUpdateHappy:
    async def test_update_role_name_200(self, admin_client, test_cast_entry):
        new_role = fake.word().title()
        r = await admin_client.put(f"{BASE}/{test_cast_entry.id}", json={"role_name": new_role})
        assert r.status_code == 200 and r.json()["role_name"] == new_role

    async def test_update_billing_order_200(self, admin_client, test_cast_entry):
        r = await admin_client.put(f"{BASE}/{test_cast_entry.id}", json={"billing_order": 5})
        assert r.status_code == 200 and r.json()["billing_order"] == 5

    async def test_update_is_lead_200(self, admin_client, test_cast_entry):
        r = await admin_client.put(f"{BASE}/{test_cast_entry.id}", json={"is_lead": True})
        assert r.status_code == 200 and r.json()["is_lead"] is True

    async def test_partial_update_retains_fields(self, admin_client, test_cast_entry):
        r = await admin_client.put(f"{BASE}/{test_cast_entry.id}", json={"billing_order": 3})
        assert r.json()["movie_id"] == str(test_cast_entry.movie_id)
