import pytest
from faker import Faker

pytestmark = pytest.mark.integration
BASE = "/api/v1/reviews"
fake = Faker()


class TestReviewsUpdateHappy:
    async def test_update_rating_200(self, user_client, test_review):
        r = await user_client.put(f"{BASE}/{test_review.id}", json={"rating": 8})
        assert r.status_code == 200 and r.json()["rating"] == 8

    async def test_update_body_200(self, user_client, test_review):
        new_body = fake.paragraph()
        r = await user_client.put(f"{BASE}/{test_review.id}", json={"body": new_body})
        assert r.status_code == 200 and r.json()["body"] == new_body

    async def test_partial_update_retains_fields(self, user_client, test_review):
        r = await user_client.put(f"{BASE}/{test_review.id}", json={"rating": 7})
        assert r.json()["movie_id"] == str(test_review.movie_id)
