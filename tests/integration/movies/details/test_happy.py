import pytest
from faker import Faker

pytestmark = pytest.mark.integration
fake = Faker()


class TestMoviesDetailsHappy:
    async def test_create_details_returns_200(self, admin_client, test_movie):
        r = await admin_client.patch(
            f"/api/v1/movies/{test_movie.id}/details", json={"synopsis": fake.paragraph()}
        )
        assert r.status_code == 200

    async def test_response_has_expected_fields(self, admin_client, test_movie):
        synopsis = fake.paragraph()
        r = await admin_client.patch(
            f"/api/v1/movies/{test_movie.id}/details", json={"synopsis": synopsis}
        )
        d = r.json()
        assert d["synopsis"] == synopsis
        assert "movie_id" in d

    async def test_upsert_updates_existing_details(self, admin_client, test_movie):
        await admin_client.patch(
            f"/api/v1/movies/{test_movie.id}/details", json={"budget_usd": 1000000}
        )
        r = await admin_client.patch(
            f"/api/v1/movies/{test_movie.id}/details", json={"budget_usd": 2000000}
        )
        assert r.status_code == 200 and r.json()["budget_usd"] == 2000000

    async def test_all_fields_optional(self, admin_client, test_movie):
        r = await admin_client.patch(f"/api/v1/movies/{test_movie.id}/details", json={})
        assert r.status_code == 200

    async def test_full_payload(self, admin_client, test_movie):
        r = await admin_client.patch(
            f"/api/v1/movies/{test_movie.id}/details",
            json={
                "synopsis": fake.paragraph(),
                "budget_usd": fake.random_int(min=1000000, max=200000000),
                "box_office_usd": fake.random_int(min=1000000, max=500000000),
                "awards_count": fake.random_int(min=0, max=10),
                "country": fake.country()[:100],
            },
        )
        assert r.status_code == 200
