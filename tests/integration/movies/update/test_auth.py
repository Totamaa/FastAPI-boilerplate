import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesUpdateAuth:
    async def test_no_api_key_401(self, client, test_movie):
        assert (
            await client.put(f"{BASE}/{test_movie.id}", json={"title": "new"})
        ).status_code == 401

    async def test_wrong_api_key_401(self, client, test_movie):
        assert (
            await client.put(
                f"{BASE}/{test_movie.id}", json={"title": "new"}, headers={"X-API-Key": "x"}
            )
        ).status_code == 401

    async def test_jwt_not_accepted_401(self, user_client, test_movie):
        assert (
            await user_client.put(f"{BASE}/{test_movie.id}", json={"title": "new"})
        ).status_code == 401
