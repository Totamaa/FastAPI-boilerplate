import pytest

from tests.factories import UserFactory

pytestmark = pytest.mark.integration
BASE = "/api/v1/users"


class TestUsersRestoreHappy:
    async def test_restore_returns_200(self, admin_client, db_session):
        user = await UserFactory.create(db_session)
        await admin_client.delete(f"{BASE}/{user.id}")
        r = await admin_client.post(f"{BASE}/{user.id}/restore")
        assert r.status_code == 200

    async def test_restored_user_accessible(self, admin_client, db_session):
        user = await UserFactory.create(db_session)
        await admin_client.delete(f"{BASE}/{user.id}")
        await admin_client.post(f"{BASE}/{user.id}/restore")
        assert (await admin_client.get(f"{BASE}/{user.id}")).status_code == 200

    async def test_restored_user_has_correct_id(self, admin_client, db_session):
        user = await UserFactory.create(db_session)
        await admin_client.delete(f"{BASE}/{user.id}")
        r = await admin_client.post(f"{BASE}/{user.id}/restore")
        assert r.json()["id"] == str(user.id)
