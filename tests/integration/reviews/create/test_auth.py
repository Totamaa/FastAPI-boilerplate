from datetime import UTC

import pytest

from tests.integration.builders import review_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/reviews"


class TestReviewsCreateAuth:
    async def test_no_auth_401(self, client, test_movie):
        assert (await client.post(BASE, json=review_payload(str(test_movie.id)))).status_code == 401

    async def test_api_key_not_accepted_401(self, admin_client, test_movie):
        assert (
            await admin_client.post(BASE, json=review_payload(str(test_movie.id)))
        ).status_code == 401

    async def test_expired_token_401(self, client, test_movie, test_user):
        from datetime import datetime, timedelta

        from jose import jwt

        from app.core.config.settings import get_settings

        s = get_settings()
        token = jwt.encode(
            {
                "sub": str(test_user.id),
                "exp": datetime.now(UTC) - timedelta(hours=1),
                "type": "access",
            },
            s.JWT_SECRET_KEY,
            algorithm=s.JWT_ALGORITHM,
        )
        r = await client.post(
            BASE,
            json=review_payload(str(test_movie.id)),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 401

    async def test_malformed_token_401(self, client, test_movie):
        r = await client.post(
            BASE,
            json=review_payload(str(test_movie.id)),
            headers={"Authorization": "Bearer not.a.jwt"},
        )
        assert r.status_code == 401
