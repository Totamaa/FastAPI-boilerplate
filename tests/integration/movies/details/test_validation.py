import pytest

from tests.integration.builders import INVALID_UUID

pytestmark = pytest.mark.integration


class TestMoviesDetailsValidation:
    async def test_negative_budget_422(self, admin_client, test_movie):
        r = await admin_client.patch(
            f"/api/v1/movies/{test_movie.id}/details", json={"budget_usd": -1}
        )
        assert r.status_code == 422

    async def test_negative_box_office_422(self, admin_client, test_movie):
        r = await admin_client.patch(
            f"/api/v1/movies/{test_movie.id}/details", json={"box_office_usd": -1}
        )
        assert r.status_code == 422

    async def test_negative_awards_count_422(self, admin_client, test_movie):
        r = await admin_client.patch(
            f"/api/v1/movies/{test_movie.id}/details", json={"awards_count": -1}
        )
        assert r.status_code == 422

    async def test_country_too_long_422(self, admin_client, test_movie):
        r = await admin_client.patch(
            f"/api/v1/movies/{test_movie.id}/details", json={"country": "x" * 101}
        )
        assert r.status_code == 422

    async def test_invalid_movie_id_format_422(self, admin_client):
        r = await admin_client.patch(f"/api/v1/movies/{INVALID_UUID}/details", json={})
        assert r.status_code == 422
