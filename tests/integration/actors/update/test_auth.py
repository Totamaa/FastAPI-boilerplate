import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"


class TestActorsUpdateAuth:
    async def test_no_api_key_401(self, client, test_actor):
        assert (
            await client.put(f"{BASE}/{test_actor.id}", json={"full_name": "x"})
        ).status_code == 401

    async def test_wrong_api_key_401(self, client, test_actor):
        assert (
            await client.put(
                f"{BASE}/{test_actor.id}", json={"full_name": "x"}, headers={"X-API-Key": "bad"}
            )
        ).status_code == 401

    async def test_jwt_not_accepted_401(self, user_client, test_actor):
        assert (
            await user_client.put(f"{BASE}/{test_actor.id}", json={"full_name": "x"})
        ).status_code == 401
