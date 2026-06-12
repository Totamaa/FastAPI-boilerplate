import logging
from uuid import UUID

from fastapi import status

from app.core.errors.exceptions.base import BusinessException


class CastEntryNotFoundException(BusinessException):
    def __init__(self, id: UUID):
        super().__init__(
            tag="SERVICE:MovieCast",
            message_front=f"Cast entry with id '{id}' not found.",
            message_log=f"CastEntry not found: id={id}",
            status_code=status.HTTP_404_NOT_FOUND,
            log_level=logging.WARNING,
        )


class CastEntryAlreadyExistsException(BusinessException):
    def __init__(self, movie_id: UUID, actor_id: UUID):
        super().__init__(
            tag="SERVICE:MovieCast",
            message_front="This actor is already in the cast for this movie.",
            message_log=f"Duplicate cast entry: movie_id={movie_id}, actor_id={actor_id}",
            status_code=status.HTTP_409_CONFLICT,
            log_level=logging.WARNING,
        )
