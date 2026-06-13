import logging

from fastapi import status

from app.core.errors.exceptions.base import BusinessException

_TAG = "AUTH:RefreshToken"


class RefreshTokenNotFoundException(BusinessException):
    def __init__(self) -> None:
        super().__init__(
            message_front="Invalid or expired refresh token.",
            message_log="Refresh token not found in DB.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            log_level=logging.WARNING,
            tag=_TAG,
        )


class RefreshTokenExpiredException(BusinessException):
    def __init__(self) -> None:
        super().__init__(
            message_front="Refresh token has expired.",
            message_log="Refresh token expires_at is in the past.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            log_level=logging.WARNING,
            tag=_TAG,
        )


class RefreshTokenRevokedException(BusinessException):
    def __init__(self) -> None:
        super().__init__(
            message_front="Session has been revoked.",
            message_log="Refresh token family is revoked (deleted_at IS NOT NULL).",
            status_code=status.HTTP_401_UNAUTHORIZED,
            log_level=logging.WARNING,
            tag=_TAG,
        )


class RefreshTokenTheftException(BusinessException):
    def __init__(self) -> None:
        super().__init__(
            message_front="Session compromised. Please log in again.",
            message_log="Refresh token theft detected: already-used token was replayed. Family revoked.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            log_level=logging.ERROR,
            tag=_TAG,
        )


class RefreshTokenFamilyOwnershipException(BusinessException):
    def __init__(self) -> None:
        super().__init__(
            message_front="Session not found.",
            message_log="Session family_id does not belong to the requesting user.",
            status_code=status.HTTP_404_NOT_FOUND,
            log_level=logging.WARNING,
            tag=_TAG,
        )
