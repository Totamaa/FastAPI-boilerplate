import logging
from uuid import UUID

from fastapi import status

from app.core.errors.exceptions.base import BusinessException


class GenreNotFoundException(BusinessException):
    def __init__(self, id: UUID):
        super().__init__(
            tag="genres",
            message_front=f"Genre with id '{id}' not found.",
            message_log=f"Genre not found: id={id}",
            status_code=status.HTTP_404_NOT_FOUND,
            log_level=logging.WARNING,
        )


class GenreConflictException(BusinessException):
    def __init__(self, field: str, value: str):
        super().__init__(
            tag="genres",
            message_front=f"Genre with {field} '{value}' already exists.",
            message_log=f"Genre conflict: {field}={value}",
            status_code=status.HTTP_409_CONFLICT,
            log_level=logging.WARNING,
        )
