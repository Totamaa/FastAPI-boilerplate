from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.logs import LoggerManager
from app.core.security.hash_lib import hash_password, verify_password
from app.modules.users.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserInactiveException,
    UserNotFoundException,
)
from app.modules.users.model import UserModel
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserLogin, UserRegister, UserResponse


class UserService:
    def __init__(
        self,
        logger: LoggerManager,
        session: AsyncSession,
        request_id: str,
        user_repository: UserRepository,
    ):
        self.tag = "SERVICE:User"
        self.logger = logger
        self.session = session
        self.request_id = request_id
        self.user_repository = user_repository

    async def get_by_id(self, id: UUID) -> UserResponse:
        user = await self.user_repository.get_by_id(id=id, db=self.session)
        if not user:
            raise UserNotFoundException(id=id)
        return UserResponse.from_model(user)

    async def register(self, data: UserRegister) -> UserModel:
        self.logger.info(
            tag=self.tag,
            message=f"Registering user email={data.email}",
            extra=self.request_id,
        )
        existing = await self.user_repository.get_by_email(email=data.email, db=self.session)
        if existing:
            raise UserAlreadyExistsException(email=data.email)

        user = UserModel(
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        return await self.user_repository.create(user=user, db=self.session)

    async def authenticate(self, data: UserLogin) -> UserModel:
        self.logger.info(
            tag=self.tag,
            message=f"Authenticating user email={data.email}",
            extra=self.request_id,
        )
        user = await self.user_repository.get_by_email(email=data.email, db=self.session)
        if not user:
            raise InvalidCredentialsException()

        is_valid, need_rehash = verify_password(data.password, user.hashed_password)
        if not is_valid:
            raise InvalidCredentialsException()

        if not user.is_active:
            raise UserInactiveException()

        if need_rehash:
            self.logger.info(
                tag=self.tag,
                message="Rehashing password for user",
                extra=self.request_id,
            )
            await self.user_repository.update(
                user=user,
                data={"hashed_password": hash_password(data.password)},
                db=self.session,
            )

        return user
