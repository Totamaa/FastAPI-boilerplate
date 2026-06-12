import pytest
from faker import Faker

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"
fake = Faker()


class TestActorsUpdateHappy:
    async def test_update_full_name_200(self, admin_client, test_actor):
        new_name = fake.name()
        r = await admin_client.put(f"{BASE}/{test_actor.id}", json={"full_name": new_name})
        assert r.status_code == 200 and r.json()["full_name"] == new_name

    async def test_update_nationality(self, admin_client, test_actor):
        country = fake.country()[:100]
        r = await admin_client.put(f"{BASE}/{test_actor.id}", json={"nationality": country})
        assert r.status_code == 200 and r.json()["nationality"] == country

    async def test_partial_update_others_unchanged(self, admin_client, test_actor):
        original_name = test_actor.full_name
        r = await admin_client.put(f"{BASE}/{test_actor.id}", json={"nationality": "FR"})
        assert r.json()["full_name"] == original_name

    async def test_extra_fields_ignored(self, admin_client, test_actor):
        assert (
            await admin_client.put(f"{BASE}/{test_actor.id}", json={"unknown": "x"})
        ).status_code == 200
