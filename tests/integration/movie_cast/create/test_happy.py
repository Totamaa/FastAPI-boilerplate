import pytest

from tests.integration.builders import cast_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/movie-cast"


class TestMovieCastCreateHappy:
    async def test_creates_entry_201(self, admin_client, test_movie, test_actor):
        r = await admin_client.post(BASE, json=cast_payload(str(test_movie.id), str(test_actor.id)))
        assert r.status_code == 201

    async def test_response_has_expected_fields(self, admin_client, test_movie, test_actor):
        p = cast_payload(str(test_movie.id), str(test_actor.id))
        r = await admin_client.post(BASE, json=p)
        d = r.json()
        assert d["movie_id"] == str(test_movie.id)
        assert d["actor_id"] == str(test_actor.id)
        assert d["role_name"] == p["role_name"]

    async def test_as_lead_role(self, admin_client, test_movie, test_actor):
        assert (
            await admin_client.post(
                BASE, json=cast_payload(str(test_movie.id), str(test_actor.id), is_lead=True)
            )
        ).status_code == 201

    async def test_extra_fields_ignored(self, admin_client, test_movie, test_actor):
        assert (
            await admin_client.post(
                BASE, json=cast_payload(str(test_movie.id), str(test_actor.id), extra="x")
            )
        ).status_code == 201
