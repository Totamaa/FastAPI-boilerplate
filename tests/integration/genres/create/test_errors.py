import pytest

from tests.integration.builders import genre_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/genres"


class TestGenresCreateErrors:
    async def test_duplicate_slug_409(self, admin_client, test_genre):
        r = await admin_client.post(BASE, json=genre_payload(slug=test_genre.slug))
        assert r.status_code == 409

    async def test_duplicate_name_409(self, admin_client, test_genre):
        r = await admin_client.post(
            BASE, json=genre_payload(name=test_genre.name, slug="different-slug")
        )
        assert r.status_code == 409
