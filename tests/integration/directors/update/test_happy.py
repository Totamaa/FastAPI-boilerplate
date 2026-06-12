import pytest
from faker import Faker

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"
fake = Faker()


class TestDirectorsUpdateHappy:
    async def test_update_full_name_200(self, admin_client, test_director):
        new_name = fake.name()
        r = await admin_client.put(f"{BASE}/{test_director.id}", json={"full_name": new_name})
        assert r.status_code == 200 and r.json()["full_name"] == new_name

    async def test_partial_update_name_unchanged(self, admin_client, test_director):
        original = test_director.full_name
        r = await admin_client.put(f"{BASE}/{test_director.id}", json={"nationality": "FR"})
        assert r.json()["full_name"] == original

    async def test_extra_fields_ignored(self, admin_client, test_director):
        assert (
            await admin_client.put(f"{BASE}/{test_director.id}", json={"unknown": "x"})
        ).status_code == 200
