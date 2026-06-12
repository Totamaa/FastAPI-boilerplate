import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/movie-cast"


class TestMovieCastDeleteAuth:
    async def test_no_auth_401(self, client, test_cast_entry):
        assert (await client.delete(f"{BASE}/{test_cast_entry.id}")).status_code == 401

    async def test_jwt_not_accepted_401(self, user_client, test_cast_entry):
        assert (await user_client.delete(f"{BASE}/{test_cast_entry.id}")).status_code == 401

    async def test_wrong_key_401(self, client, test_cast_entry):
        headers = {"X-API-Key": "wrong"}
        assert (
            await client.delete(f"{BASE}/{test_cast_entry.id}", headers=headers)
        ).status_code == 401
