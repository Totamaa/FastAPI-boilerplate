from app.core.config.logs import LoggerManager
from app.core.security.jwt_lib import create_access_token, create_refresh_token
from app.modules.users.schemas import TokenResponse, UserLogin, UserRegister, UserResponse
from app.modules.users.service import UserService


class AuthService:
    def __init__(self, logger: LoggerManager, user_service: UserService) -> None:
        self.tag = "SERVICE:Auth"
        self.logger = logger
        self.user_service = user_service

    async def register(self, data: UserRegister) -> UserResponse:
        user = await self.user_service.register(data)
        self.logger.info(self.tag, f"Registered user id={user.id}")
        return UserResponse.from_model(user)

    async def login(self, data: UserLogin) -> TokenResponse:
        user = await self.user_service.authenticate(data)
        self.logger.info(self.tag, f"Logged in user id={user.id}")
        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
