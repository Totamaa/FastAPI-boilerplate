import pytest

from tests.integration.builders import director_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"


class TestDirectorsCreateAuth:
    async def test_no_api_key_401(self, client):
        assert (await client.post(BASE, json=director_payload())).status_code == 401

    async def test_wrong_key_401(self, client):
        assert (
            await client.post(BASE, json=director_payload(), headers={"X-API-Key": "bad"})
        ).status_code == 401

    async def test_jwt_not_accepted_401(self, user_client):
        assert (await user_client.post(BASE, json=director_payload())).status_code == 401
