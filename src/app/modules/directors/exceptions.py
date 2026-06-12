import logging
from uuid import UUID

from fastapi import status

from app.core.errors.exceptions.base import BusinessException


class DirectorNotFoundException(BusinessException):
    def __init__(self, id: UUID):
        super().__init__(
            tag="directors",
            message_front=f"Director with id '{id}' not found.",
            message_log=f"Director not found: id={id}",
            status_code=status.HTTP_404_NOT_FOUND,
            log_level=logging.WARNING,
        )
