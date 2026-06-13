import pytest

from tests.factories.feature_flag import FeatureFlagFactory


@pytest.fixture
async def test_flag(db_session):
    return await FeatureFlagFactory.create(
        db_session,
        key="test:sample_flag",
        enabled=True,
        rollout_percentage=50,
        description="Integration test flag",
    )
