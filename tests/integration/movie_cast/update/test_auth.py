import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/movie-cast"


class TestMovieCastUpdateAuth:
    async def test_no_auth_401(self, client, test_cast_entry):
        assert (
            await client.put(f"{BASE}/{test_cast_entry.id}", json={"billing_order": 3})
        ).status_code == 401

    async def test_jwt_not_accepted_401(self, user_client, test_cast_entry):
        assert (
            await user_client.put(f"{BASE}/{test_cast_entry.id}", json={"billing_order": 3})
        ).status_code == 401
