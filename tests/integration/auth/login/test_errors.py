import pytest
from faker import Faker

pytestmark = pytest.mark.integration
BASE = "/api/v1/auth/login"
fake = Faker()


class TestLoginErrors:
    async def test_wrong_password_401(self, client, test_user):
        r = await client.post(BASE, data={"username": test_user.email, "password": "WrongPass1!"})
        assert r.status_code == 401

    async def test_unknown_email_401(self, client):
        r = await client.post(BASE, data={"username": fake.email(), "password": "Testpass1!"})
        assert r.status_code == 401

    async def test_inactive_user_403(self, client, db_session):
        from app.core.security.hash_lib import hash_password
        from app.modules.users.model import UserModel

        user = UserModel(
            email=fake.email(), hashed_password=hash_password("Testpass1!"), is_active=False
        )
        db_session.add(user)
        await db_session.flush()
        r = await client.post(BASE, data={"username": user.email, "password": "Testpass1!"})
        assert r.status_code == 403
