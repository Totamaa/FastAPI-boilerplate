import pytest
from sqlalchemy import update

from app.modules.feature_flags.model import FeatureFlagModel

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesListErrors:
    async def test_status_filter_with_no_match_returns_empty_list(self, client):
        r = await client.get(BASE, params={"status": "upcoming"})
        assert r.status_code == 200 and r.json() == []

    async def test_listing_disabled_returns_503(self, client, db_session):
        await db_session.execute(
            update(FeatureFlagModel)
            .where(FeatureFlagModel.key == "movies:listing_enabled")
            .values(enabled=False)
        )
        await db_session.flush()
        r = await client.get(BASE)
        assert r.status_code == 503
