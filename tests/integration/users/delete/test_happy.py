import pytest

from tests.factories import UserFactory

pytestmark = pytest.mark.integration
BASE = "/api/v1/users"
REVIEWS_BASE = "/api/v1/reviews"
AUTH_REGISTER = "/api/v1/auth/register"


class TestUsersDeleteHappy:
    async def test_delete_returns_204(self, admin_client, test_user):
        assert (await admin_client.delete(f"{BASE}/{test_user.id}")).status_code == 204

    async def test_user_not_accessible_after_delete(self, admin_client, test_user):
        await admin_client.delete(f"{BASE}/{test_user.id}")
        assert (await admin_client.get(f"{BASE}/{test_user.id}")).status_code == 404

    async def test_email_anonymized_on_delete(self, admin_client, db_session):
        user = await UserFactory.create(db_session)
        original_email = user.email
        await admin_client.delete(f"{BASE}/{user.id}")
        await db_session.refresh(user)
        assert user.email != original_email
        assert user.email.endswith("@deleted.local")

    async def test_password_redacted_on_delete(self, admin_client, db_session):
        user = await UserFactory.create(db_session)
        await admin_client.delete(f"{BASE}/{user.id}")
        await db_session.refresh(user)
        assert user.hashed_password == "REDACTED"

    async def test_delete_user_soft_deletes_reviews(
        self, admin_client, client, test_user, test_movie, test_review
    ):
        await admin_client.delete(f"{BASE}/{test_user.id}")
        r = await client.get(REVIEWS_BASE, params={"movie_id": str(test_movie.id)})
        assert r.status_code == 200
        assert r.json() == []

    async def test_deleted_email_can_be_reused(self, admin_client, client, db_session):
        user = await UserFactory.create(db_session)
        email = user.email
        await admin_client.delete(f"{BASE}/{user.id}")
        r = await client.post(
            AUTH_REGISTER,
            json={"email": email, "password": "Testpass1!", "password_confirm": "Testpass1!"},
        )
        assert r.status_code == 201
