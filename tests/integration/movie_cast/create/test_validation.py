import pytest

from tests.integration.builders import INVALID_UUID, cast_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/movie-cast"


class TestMovieCastCreateValidation:
    async def test_missing_movie_id_422(self, admin_client, test_movie, test_actor):
        p = {
            k: v
            for k, v in cast_payload(str(test_movie.id), str(test_actor.id)).items()
            if k != "movie_id"
        }
        assert (await admin_client.post(BASE, json=p)).status_code == 422

    async def test_missing_actor_id_422(self, admin_client, test_movie, test_actor):
        p = {
            k: v
            for k, v in cast_payload(str(test_movie.id), str(test_actor.id)).items()
            if k != "actor_id"
        }
        assert (await admin_client.post(BASE, json=p)).status_code == 422

    async def test_invalid_movie_id_422(self, admin_client, test_actor):
        assert (
            await admin_client.post(BASE, json=cast_payload(INVALID_UUID, str(test_actor.id)))
        ).status_code == 422

    async def test_invalid_actor_id_422(self, admin_client, test_movie):
        assert (
            await admin_client.post(BASE, json=cast_payload(str(test_movie.id), INVALID_UUID))
        ).status_code == 422

    async def test_billing_order_below_1_422(self, admin_client, test_movie, test_actor):
        assert (
            await admin_client.post(
                BASE, json=cast_payload(str(test_movie.id), str(test_actor.id), billing_order=0)
            )
        ).status_code == 422

    async def test_missing_role_name_422(self, admin_client, test_movie, test_actor):
        p = {
            k: v
            for k, v in cast_payload(str(test_movie.id), str(test_actor.id)).items()
            if k != "role_name"
        }
        assert (await admin_client.post(BASE, json=p)).status_code == 422

    async def test_empty_body_422(self, admin_client):
        assert (await admin_client.post(BASE, json={})).status_code == 422
