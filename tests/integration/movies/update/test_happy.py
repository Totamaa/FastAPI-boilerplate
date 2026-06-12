import pytest
from faker import Faker

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"
fake = Faker()


class TestMoviesUpdateHappy:
    async def test_update_title_returns_200(self, admin_client, test_movie):
        new_title = " ".join(fake.words(3)).title()
        r = await admin_client.put(f"{BASE}/{test_movie.id}", json={"title": new_title})
        assert r.status_code == 200 and r.json()["title"] == new_title

    async def test_update_release_year(self, admin_client, test_movie):
        year = fake.random_int(min=1950, max=2024)
        r = await admin_client.put(f"{BASE}/{test_movie.id}", json={"release_year": year})
        assert r.status_code == 200 and r.json()["release_year"] == year

    async def test_update_status(self, admin_client, test_movie):
        r = await admin_client.put(f"{BASE}/{test_movie.id}", json={"status": "upcoming"})
        assert r.status_code == 200 and r.json()["status"] == "upcoming"

    async def test_partial_update_other_fields_unchanged(self, admin_client, test_movie):
        original_year = test_movie.release_year
        r = await admin_client.put(f"{BASE}/{test_movie.id}", json={"status": "released"})
        assert r.json()["release_year"] == original_year

    async def test_extra_fields_ignored(self, admin_client, test_movie):
        r = await admin_client.put(f"{BASE}/{test_movie.id}", json={"unknown": "value"})
        assert r.status_code == 200
