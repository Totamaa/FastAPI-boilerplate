from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.hash_lib import hash_password
from app.modules.users.model import UserModel

fake = Faker()


class UserFactory:
    @staticmethod
    async def create(session: AsyncSession, **kwargs) -> UserModel:
        user = UserModel(
            email=kwargs.get("email", fake.unique.email()),
            hashed_password=hash_password(kwargs.get("password", "Testpass1!")),
            is_active=kwargs.get("is_active", True),
            is_admin=kwargs.get("is_admin", False),
        )
        session.add(user)
        await session.flush()
        return user
