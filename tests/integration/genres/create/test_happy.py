import pytest

from tests.integration.builders import genre_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/genres"


class TestGenresCreateHappy:
    async def test_creates_genre_201(self, admin_client):
        r = await admin_client.post(BASE, json=genre_payload())
        assert r.status_code == 201

    async def test_response_has_expected_fields(self, admin_client):
        p = genre_payload()
        r = await admin_client.post(BASE, json=p)
        d = r.json()
        assert d["name"] == p["name"] and d["slug"] == p["slug"]
        assert "id" in d

    async def test_with_description(self, admin_client):
        from faker import Faker

        r = await admin_client.post(BASE, json=genre_payload(description=Faker().sentence()))
        assert r.status_code == 201

    async def test_extra_fields_ignored(self, admin_client):
        assert (await admin_client.post(BASE, json=genre_payload(extra="x"))).status_code == 201
