import pytest

from tests.factories import DirectorFactory, GenreFactory
from tests.integration.builders import movie_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesCreateHappy:
    async def test_minimal_payload_returns_201(self, admin_client):
        assert (await admin_client.post(BASE, json=movie_payload())).status_code == 201

    async def test_response_has_expected_fields(self, admin_client):
        p = movie_payload()
        r = await admin_client.post(BASE, json=p)
        d = r.json()
        assert d["title"] == p["title"] and d["release_year"] == p["release_year"]
        assert "id" in d and "created_at" in d

    async def test_create_with_director(self, admin_client, db_session):
        director = await DirectorFactory.create(db_session)
        r = await admin_client.post(BASE, json=movie_payload(director_id=str(director.id)))
        assert r.status_code == 201 and r.json()["director_id"] == str(director.id)

    async def test_create_with_genre_ids(self, admin_client, db_session):
        genre = await GenreFactory.create(db_session)
        assert (
            await admin_client.post(BASE, json=movie_payload(genre_ids=[str(genre.id)]))
        ).status_code == 201

    async def test_create_with_full_payload(self, admin_client, db_session):
        director = await DirectorFactory.create(db_session)
        genre = await GenreFactory.create(db_session)
        p = movie_payload(
            director_id=str(director.id),
            genre_ids=[str(genre.id)],
            duration_minutes=120,
            language="en",
            status="upcoming",
        )
        assert (await admin_client.post(BASE, json=p)).status_code == 201

    async def test_extra_fields_ignored(self, admin_client):
        assert (
            await admin_client.post(BASE, json=movie_payload(unknown_field="ignored"))
        ).status_code == 201
