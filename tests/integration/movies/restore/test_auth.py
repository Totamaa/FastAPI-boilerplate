import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesRestoreAuth:
    async def test_no_api_key_401(self, client, test_movie):
        assert (await client.post(f"{BASE}/{test_movie.id}/restore")).status_code == 401

    async def test_jwt_not_accepted_401(self, user_client, test_movie):
        assert (await user_client.post(f"{BASE}/{test_movie.id}/restore")).status_code == 401
