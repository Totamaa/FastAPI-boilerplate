import logging

from fastapi import status

from app.core.errors.exceptions.base import BusinessException


class FeatureFlagNotFoundException(BusinessException):
    def __init__(self, key: str) -> None:
        super().__init__(
            tag="feature_flags",
            message_front=f"Feature flag '{key}' not found.",
            message_log=f"Feature flag not found: key={key}",
            status_code=status.HTTP_404_NOT_FOUND,
            log_level=logging.WARNING,
        )


class FeatureFlagConflictException(BusinessException):
    def __init__(self, key: str) -> None:
        super().__init__(
            tag="feature_flags",
            message_front=f"Feature flag '{key}' already exists.",
            message_log=f"Feature flag conflict: key={key}",
            status_code=status.HTTP_409_CONFLICT,
            log_level=logging.WARNING,
        )


class FeatureDisabledException(BusinessException):
    def __init__(self, key: str) -> None:
        super().__init__(
            tag="feature_flags",
            message_front=f"Feature '{key}' is currently unavailable.",
            message_log=f"Feature disabled: key={key}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            log_level=logging.INFO,
        )
