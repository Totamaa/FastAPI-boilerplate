import pytest
from sqlalchemy import select

from app.modules.movie_cast.model import MovieCastModel

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"


class TestActorsDeleteCascade:
    async def test_delete_actor_soft_deletes_cast_entries(
        self, admin_client, db_session, test_cast_entry
    ):
        actor_id = test_cast_entry.actor_id
        await admin_client.delete(f"{BASE}/{actor_id}")
        result = await db_session.execute(
            select(MovieCastModel)
            .where(MovieCastModel.actor_id == actor_id)
            .execution_options(include_deleted=True, populate_existing=True)
        )
        entries = result.scalars().all()
        assert len(entries) > 0
        assert all(e.deleted_at is not None for e in entries)
