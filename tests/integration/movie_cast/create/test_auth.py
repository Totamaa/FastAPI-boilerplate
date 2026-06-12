import pytest

from tests.integration.builders import cast_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/movie-cast"


class TestMovieCastCreateAuth:
    async def test_no_auth_401(self, client, test_movie, test_actor):
        assert (
            await client.post(BASE, json=cast_payload(str(test_movie.id), str(test_actor.id)))
        ).status_code == 401

    async def test_jwt_not_accepted_401(self, user_client, test_movie, test_actor):
        assert (
            await user_client.post(BASE, json=cast_payload(str(test_movie.id), str(test_actor.id)))
        ).status_code == 401

    async def test_wrong_key_401(self, client, test_movie, test_actor):
        headers = {"X-API-Key": "bad-key"}
        assert (
            await client.post(
                BASE, json=cast_payload(str(test_movie.id), str(test_actor.id)), headers=headers
            )
        ).status_code == 401
