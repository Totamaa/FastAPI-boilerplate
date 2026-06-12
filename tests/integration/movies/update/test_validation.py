import pytest

from tests.integration.builders import INVALID_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesUpdateValidation:
    async def test_title_too_long_422(self, admin_client, test_movie):
        assert (
            await admin_client.put(f"{BASE}/{test_movie.id}", json={"title": "t" * 501})
        ).status_code == 422

    async def test_empty_title_422(self, admin_client, test_movie):
        assert (
            await admin_client.put(f"{BASE}/{test_movie.id}", json={"title": ""})
        ).status_code == 422

    async def test_release_year_before_1888_422(self, admin_client, test_movie):
        assert (
            await admin_client.put(f"{BASE}/{test_movie.id}", json={"release_year": 1887})
        ).status_code == 422

    async def test_release_year_after_2100_422(self, admin_client, test_movie):
        assert (
            await admin_client.put(f"{BASE}/{test_movie.id}", json={"release_year": 2101})
        ).status_code == 422

    async def test_invalid_status_value_422(self, admin_client, test_movie):
        assert (
            await admin_client.put(f"{BASE}/{test_movie.id}", json={"status": "bad"})
        ).status_code == 422

    async def test_invalid_id_format_422(self, admin_client):
        assert (
            await admin_client.put(f"{BASE}/{INVALID_UUID}", json={"title": "x"})
        ).status_code == 422
