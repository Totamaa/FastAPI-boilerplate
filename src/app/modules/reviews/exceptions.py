import logging
from uuid import UUID

from fastapi import status

from app.core.errors.exceptions.base import BusinessException


class ReviewNotFoundException(BusinessException):
    def __init__(self, id: UUID):
        super().__init__(
            tag="SERVICE:Review",
            message_front="Review not found.",
            message_log=f"Review not found: id={id}",
            status_code=status.HTTP_404_NOT_FOUND,
            log_level=logging.WARNING,
        )


class ReviewAlreadyExistsException(BusinessException):
    def __init__(self, movie_id: UUID):
        super().__init__(
            tag="SERVICE:Review",
            message_front="You already reviewed this movie.",
            message_log=f"Duplicate review attempt: movie_id={movie_id}",
            status_code=status.HTTP_409_CONFLICT,
            log_level=logging.WARNING,
        )


class ReviewForbiddenException(BusinessException):
    def __init__(self):
        super().__init__(
            tag="SERVICE:Review",
            message_front="You can only modify your own reviews.",
            message_log="Forbidden review modification attempt.",
            status_code=status.HTTP_403_FORBIDDEN,
            log_level=logging.WARNING,
        )
