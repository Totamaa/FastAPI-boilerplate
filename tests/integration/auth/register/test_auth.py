import pytest

from tests.integration.builders import user_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/auth/register"


class TestRegisterAuth:
    async def test_endpoint_is_public(self, client):
        assert (await client.post(BASE, json=user_payload())).status_code == 201

    async def test_works_with_api_key_header(self, admin_client):
        assert (await admin_client.post(BASE, json=user_payload())).status_code == 201

    async def test_works_while_jwt_authenticated(self, user_client):
        assert (await user_client.post(BASE, json=user_payload())).status_code == 201
