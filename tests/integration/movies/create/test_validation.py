import pytest
from faker import Faker

from tests.integration.builders import INVALID_UUID, movie_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"
fake = Faker()


class TestMoviesCreateValidation:
    async def test_missing_title_422(self, admin_client):
        p = {k: v for k, v in movie_payload().items() if k != "title"}
        assert (await admin_client.post(BASE, json=p)).status_code == 422

    async def test_empty_title_422(self, admin_client):
        assert (await admin_client.post(BASE, json=movie_payload(title=""))).status_code == 422

    async def test_title_too_long_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=movie_payload(title="t" * 501))
        ).status_code == 422

    async def test_missing_release_year_422(self, admin_client):
        p = {k: v for k, v in movie_payload().items() if k != "release_year"}
        assert (await admin_client.post(BASE, json=p)).status_code == 422

    async def test_release_year_before_1888_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=movie_payload(release_year=1887))
        ).status_code == 422

    async def test_release_year_after_2100_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=movie_payload(release_year=2101))
        ).status_code == 422

    async def test_duration_below_1_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=movie_payload(duration_minutes=0))
        ).status_code == 422

    async def test_duration_above_600_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=movie_payload(duration_minutes=601))
        ).status_code == 422

    async def test_language_too_long_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=movie_payload(language="toolong"))
        ).status_code == 422

    async def test_invalid_status_value_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=movie_payload(status="bad_status"))
        ).status_code == 422

    async def test_invalid_director_id_format_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=movie_payload(director_id=INVALID_UUID))
        ).status_code == 422

    async def test_invalid_genre_id_format_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=movie_payload(genre_ids=[INVALID_UUID]))
        ).status_code == 422

    async def test_empty_body_422(self, admin_client):
        assert (await admin_client.post(BASE, json={})).status_code == 422
