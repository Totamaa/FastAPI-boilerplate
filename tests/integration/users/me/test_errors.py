import pytest
from faker import Faker

pytestmark = pytest.mark.integration
BASE = "/api/v1/users/me"
fake = Faker()


class TestUsersMeErrors:
    async def test_deactivated_user_401(self, client, db_session):
        from app.core.security.hash_lib import hash_password
        from app.core.security.jwt_lib import create_access_token
        from app.modules.users.model import UserModel

        user = UserModel(
            email=fake.email(), hashed_password=hash_password("Testpass1!"), is_active=False
        )
        db_session.add(user)
        await db_session.flush()
        token = create_access_token(user.id)
        assert (
            await client.get(BASE, headers={"Authorization": f"Bearer {token}"})
        ).status_code == 401
