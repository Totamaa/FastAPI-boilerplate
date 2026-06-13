from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from jose import jwt

from app.core.config.settings import get_settings
from app.core.errors.exceptions.auth import (
    JWTExpiredException,
    JWTInvalidSignatureException,
)
from app.core.security.jwt_lib import (
    TokenPayload,
    create_access_token,
    decode_token,
)


@pytest.mark.unit
class TestCreateTokens:
    def test_create_access_token_returns_string(self):
        token = create_access_token(uuid4())
        assert isinstance(token, str) and len(token) > 0

    def test_access_token_has_correct_type(self):
        user_id = uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token)
        assert payload.type == "access"

    def test_token_sub_matches_user_id(self):
        user_id = uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token)
        assert payload.sub == str(user_id)


@pytest.mark.unit
class TestDecodeToken:
    def test_returns_token_payload_instance(self):
        token = create_access_token(uuid4())
        payload = decode_token(token)
        assert isinstance(payload, TokenPayload)

    def test_raises_jwt_expired_on_expired_token(self):
        settings = get_settings()
        expired_payload = {
            "sub": str(uuid4()),
            "exp": datetime.now(UTC) - timedelta(seconds=1),
            "type": "access",
        }
        token = jwt.encode(
            expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        with pytest.raises(JWTExpiredException):
            decode_token(token)

    def test_raises_jwt_invalid_signature_on_wrong_secret(self):
        user_id = uuid4()
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(UTC) + timedelta(minutes=30),
            "type": "access",
        }
        token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
        with pytest.raises(JWTInvalidSignatureException):
            decode_token(token)

    def test_raises_jwt_invalid_signature_on_malformed_token(self):
        with pytest.raises(JWTInvalidSignatureException):
            decode_token("not.a.valid.token")

    def test_raises_jwt_invalid_on_payload_missing_required_field(self):
        settings = get_settings()
        incomplete_payload = {
            "sub": str(uuid4()),
            "exp": datetime.now(UTC) + timedelta(minutes=30),
            # missing "type"
        }
        token = jwt.encode(
            incomplete_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        with pytest.raises(JWTInvalidSignatureException):
            decode_token(token)
