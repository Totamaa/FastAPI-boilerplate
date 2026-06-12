import pytest

pytestmark = pytest.mark.integration


class TestMoviesDetailsAuth:
    async def test_no_api_key_401(self, client, test_movie):
        assert (
            await client.patch(f"/api/v1/movies/{test_movie.id}/details", json={})
        ).status_code == 401

    async def test_wrong_api_key_401(self, client, test_movie):
        assert (
            await client.patch(
                f"/api/v1/movies/{test_movie.id}/details", json={}, headers={"X-API-Key": "x"}
            )
        ).status_code == 401

    async def test_jwt_not_accepted_401(self, user_client, test_movie):
        assert (
            await user_client.patch(f"/api/v1/movies/{test_movie.id}/details", json={})
        ).status_code == 401
