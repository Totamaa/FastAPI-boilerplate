import pytest

from tests.integration.builders import genre_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/genres"


class TestGenresCreateValidation:
    async def test_missing_name_422(self, admin_client):
        p = {k: v for k, v in genre_payload().items() if k != "name"}
        assert (await admin_client.post(BASE, json=p)).status_code == 422

    async def test_empty_name_422(self, admin_client):
        assert (await admin_client.post(BASE, json=genre_payload(name=""))).status_code == 422

    async def test_name_too_long_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=genre_payload(name="a" * 101))
        ).status_code == 422

    async def test_missing_slug_422(self, admin_client):
        p = {k: v for k, v in genre_payload().items() if k != "slug"}
        assert (await admin_client.post(BASE, json=p)).status_code == 422

    async def test_empty_slug_422(self, admin_client):
        assert (await admin_client.post(BASE, json=genre_payload(slug=""))).status_code == 422

    async def test_slug_too_long_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=genre_payload(slug="a" * 101))
        ).status_code == 422

    async def test_slug_with_uppercase_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=genre_payload(slug="Invalid-Slug"))
        ).status_code == 422

    async def test_slug_with_spaces_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=genre_payload(slug="invalid slug"))
        ).status_code == 422

    async def test_slug_with_special_chars_422(self, admin_client):
        assert (
            await admin_client.post(BASE, json=genre_payload(slug="invalid@slug"))
        ).status_code == 422

    async def test_empty_body_422(self, admin_client):
        assert (await admin_client.post(BASE, json={})).status_code == 422
