import pytest

from tests.integration.builders import movie_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesCreateAuth:
    async def test_no_api_key_401(self, client):
        assert (await client.post(BASE, json=movie_payload())).status_code == 401

    async def test_wrong_api_key_401(self, client):
        assert (
            await client.post(BASE, json=movie_payload(), headers={"X-API-Key": "wrong"})
        ).status_code == 401

    async def test_jwt_token_not_accepted_401(self, user_client):
        assert (await user_client.post(BASE, json=movie_payload())).status_code == 401
