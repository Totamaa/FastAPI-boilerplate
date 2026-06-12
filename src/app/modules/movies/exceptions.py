import logging
from uuid import UUID

from fastapi import status

from app.core.errors.exceptions.base import BusinessException


class MovieNotFoundException(BusinessException):
    def __init__(self, id: UUID):
        super().__init__(
            tag="SERVICE:Movie",
            message_front=f"Movie with id '{id}' not found.",
            message_log=f"Movie not found: id={id}",
            status_code=status.HTTP_404_NOT_FOUND,
            log_level=logging.WARNING,
        )
