import logging
from uuid import UUID

from fastapi import status

from app.core.errors.exceptions.base import BusinessException


class MovieDetailNotFoundException(BusinessException):
    def __init__(self, movie_id: UUID):
        super().__init__(
            tag="SERVICE:MovieDetail",
            message_front=f"Movie detail for movie id '{movie_id}' not found.",
            message_log=f"MovieDetail not found: movie_id={movie_id}",
            status_code=status.HTTP_404_NOT_FOUND,
            log_level=logging.WARNING,
        )
