import logging

from fastapi import status

from app.core.errors.exceptions.base import BusinessException

_TAG = "AUTH:JWT"


class JWTExpiredException(BusinessException):
    def __init__(self) -> None:
        super().__init__(
            message_front="Token has expired.",
            message_log="JWT ExpiredSignatureError: access token has expired.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            log_level=logging.WARNING,
            tag=_TAG,
        )


class JWTInvalidSignatureException(BusinessException):
    def __init__(self) -> None:
        super().__init__(
            message_front="Invalid token.",
            message_log="JWT JWTError: invalid signature or malformed token.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            log_level=logging.WARNING,
            tag=_TAG,
        )


class JWTWrongTypeException(BusinessException):
    def __init__(self, expected: str, got: str) -> None:
        super().__init__(
            message_front="Invalid token.",
            message_log=f"JWT wrong token type: expected '{expected}', received '{got}'.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            log_level=logging.WARNING,
            tag=_TAG,
        )


class JWTMissingSubjectException(BusinessException):
    def __init__(self) -> None:
        super().__init__(
            message_front="Invalid token.",
            message_log="JWT payload is missing 'sub' field or it is not a valid UUID.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            log_level=logging.WARNING,
            tag=_TAG,
        )
