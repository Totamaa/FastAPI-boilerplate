import pytest

from tests.factories import MovieFactory, ReviewFactory

pytestmark = pytest.mark.integration
BASE = "/api/v1/reviews"


class TestReviewsListHappy:
    async def test_empty_list_200(self, client, test_movie):
        r = await client.get(BASE, params={"movie_id": str(test_movie.id)})
        assert r.status_code == 200 and r.json() == []

    async def test_returns_reviews(self, client, test_review, test_movie):
        r = await client.get(BASE, params={"movie_id": str(test_movie.id)})
        assert r.status_code == 200 and len(r.json()) >= 1

    async def test_only_returns_movie_reviews(
        self, client, db_session, test_user, test_review, test_movie
    ):
        other_movie = await MovieFactory.create(db_session)
        await ReviewFactory.create(db_session, user_id=test_user.id, movie_id=other_movie.id)
        r = await client.get(BASE, params={"movie_id": str(test_movie.id)})
        assert all(rv["movie_id"] == str(test_movie.id) for rv in r.json())

    async def test_limit_respected(self, client, db_session, test_user, test_movie):
        from tests.factories import UserFactory

        users = [await UserFactory.create(db_session) for _ in range(5)]
        for u in users:
            await ReviewFactory.create(db_session, user_id=u.id, movie_id=test_movie.id)
        r = await client.get(BASE, params={"movie_id": str(test_movie.id), "limit": 2})
        assert len(r.json()) == 2
