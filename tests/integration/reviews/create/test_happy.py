import pytest

from tests.integration.builders import review_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/reviews"


class TestReviewsCreateHappy:
    async def test_creates_review_201(self, user_client, test_movie):
        r = await user_client.post(BASE, json=review_payload(str(test_movie.id)))
        assert r.status_code == 201

    async def test_response_has_expected_fields(self, user_client, test_movie, test_user):
        p = review_payload(str(test_movie.id))
        r = await user_client.post(BASE, json=p)
        d = r.json()
        assert d["movie_id"] == str(test_movie.id)
        assert d["rating"] == p["rating"]
        assert d["user_id"] == str(test_user.id)

    async def test_with_body(self, user_client, test_movie):
        from faker import Faker

        p = review_payload(str(test_movie.id), body=Faker().paragraph())
        assert (await user_client.post(BASE, json=p)).status_code == 201

    async def test_extra_fields_ignored(self, user_client, test_movie):
        assert (
            await user_client.post(BASE, json=review_payload(str(test_movie.id), extra="x"))
        ).status_code == 201
