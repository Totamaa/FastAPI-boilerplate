import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/genres"


class TestGenresDeleteAuth:
    async def test_no_api_key_401(self, client, test_genre):
        assert (await client.delete(f"{BASE}/{test_genre.id}")).status_code == 401

    async def test_jwt_not_accepted_401(self, user_client, test_genre):
        assert (await user_client.delete(f"{BASE}/{test_genre.id}")).status_code == 401
