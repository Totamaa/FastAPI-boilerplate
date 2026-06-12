import logging
from uuid import UUID

from fastapi import status

from app.core.errors.exceptions.base import BusinessException


class UserNotFoundException(BusinessException):
    def __init__(self, id: UUID = None, email: str = None):
        detail = f"id={id}" if id is not None else f"email={email}"
        super().__init__(
            tag="SERVICE:User",
            message_front="User not found.",
            message_log=f"User not found: {detail}",
            status_code=status.HTTP_404_NOT_FOUND,
            log_level=logging.WARNING,
        )


class UserAlreadyExistsException(BusinessException):
    def __init__(self, email: str):
        super().__init__(
            tag="SERVICE:User",
            message_front="A user with this email already exists.",
            message_log=f"User already exists: email={email}",
            status_code=status.HTTP_409_CONFLICT,
            log_level=logging.WARNING,
        )


class InvalidCredentialsException(BusinessException):
    def __init__(self):
        super().__init__(
            tag="SERVICE:User",
            message_front="Invalid email or password.",
            message_log="Authentication failed: invalid credentials.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            log_level=logging.WARNING,
        )


class UserInactiveException(BusinessException):
    def __init__(self):
        super().__init__(
            tag="SERVICE:User",
            message_front="Account is deactivated.",
            message_log="Authentication failed: user account is inactive.",
            status_code=status.HTTP_403_FORBIDDEN,
            log_level=logging.WARNING,
        )
