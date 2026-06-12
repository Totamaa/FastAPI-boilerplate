import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesDeleteAuth:
    async def test_no_api_key_401(self, client, test_movie):
        assert (await client.delete(f"{BASE}/{test_movie.id}")).status_code == 401

    async def test_wrong_api_key_401(self, client, test_movie):
        assert (
            await client.delete(f"{BASE}/{test_movie.id}", headers={"X-API-Key": "x"})
        ).status_code == 401

    async def test_jwt_not_accepted_401(self, user_client, test_movie):
        assert (await user_client.delete(f"{BASE}/{test_movie.id}")).status_code == 401
