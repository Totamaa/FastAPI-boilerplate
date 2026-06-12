import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesGetAuth:
    async def test_public_no_auth_needed(self, client, test_movie):
        assert (await client.get(f"{BASE}/{test_movie.id}")).status_code == 200

    async def test_also_works_with_api_key(self, admin_client, test_movie):
        assert (await admin_client.get(f"{BASE}/{test_movie.id}")).status_code == 200

    async def test_also_works_authenticated(self, user_client, test_movie):
        assert (await user_client.get(f"{BASE}/{test_movie.id}")).status_code == 200
