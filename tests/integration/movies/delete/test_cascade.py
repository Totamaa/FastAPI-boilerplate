import pytest
from sqlalchemy import select

from app.modules.movie_cast.model import MovieCastModel

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"
REVIEWS_BASE = "/api/v1/reviews"


class TestMoviesDeleteCascade:
    async def test_delete_movie_soft_deletes_reviews(
        self, admin_client, client, test_movie, test_review
    ):
        await admin_client.delete(f"{BASE}/{test_movie.id}")
        r = await client.get(REVIEWS_BASE, params={"movie_id": str(test_movie.id)})
        assert r.status_code == 200
        assert r.json() == []

    async def test_delete_movie_soft_deletes_cast_entries(
        self, admin_client, db_session, test_movie, test_cast_entry
    ):
        await admin_client.delete(f"{BASE}/{test_movie.id}")
        result = await db_session.execute(
            select(MovieCastModel)
            .where(MovieCastModel.movie_id == test_movie.id)
            .execution_options(include_deleted=True, populate_existing=True)
        )
        entries = result.scalars().all()
        assert len(entries) > 0
        assert all(e.deleted_at is not None for e in entries)
