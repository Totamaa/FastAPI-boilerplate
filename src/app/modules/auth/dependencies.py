from fastapi import Depends

from app.core.config.logs import get_logger
from app.modules.auth.service import AuthService
from app.modules.users.dependencies import get_user_service
from app.modules.users.service import UserService


def get_auth_service(
    logger=Depends(get_logger),
    user_service: UserService = Depends(get_user_service),
) -> AuthService:
    return AuthService(logger=logger, user_service=user_service)
