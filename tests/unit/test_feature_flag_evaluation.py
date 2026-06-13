import hashlib
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.modules.feature_flags.repository import FeatureFlagRepository
from app.modules.feature_flags.schemas import FeatureFlagResponse

pytestmark = pytest.mark.unit

_NOW = datetime.now(UTC)


def _flag(**kwargs) -> FeatureFlagResponse:
    defaults = {
        "key": "test:flag",
        "enabled": True,
        "rollout_percentage": 100,
        "allowed_user_ids": [],
        "description": None,
        "updated_at": _NOW,
    }
    return FeatureFlagResponse(**{**defaults, **kwargs})


class TestFeatureFlagEvaluation:
    def test_disabled_flag_returns_false(self):
        flag = _flag(enabled=False, rollout_percentage=100)
        assert FeatureFlagRepository.is_enabled_for(flag, uuid4()) is False

    def test_user_in_allowed_ids_returns_true(self):
        uid = uuid4()
        flag = _flag(enabled=True, rollout_percentage=0, allowed_user_ids=[uid])
        assert FeatureFlagRepository.is_enabled_for(flag, uid) is True

    def test_user_in_rollout_returns_true(self):
        key = "test:flag"
        for _ in range(1000):
            uid = uuid4()
            h = int(hashlib.md5(f"{uid}{key}".encode()).hexdigest(), 16) % 100  # noqa: S324
            if h < 50:
                flag = _flag(enabled=True, rollout_percentage=50)
                assert FeatureFlagRepository.is_enabled_for(flag, uid) is True
                return
        pytest.fail("Could not find a user within rollout in 1000 attempts")

    def test_user_outside_rollout_returns_false(self):
        key = "test:flag"
        for _ in range(1000):
            uid = uuid4()
            h = int(hashlib.md5(f"{uid}{key}".encode()).hexdigest(), 16) % 100  # noqa: S324
            if h >= 50:
                flag = _flag(enabled=True, rollout_percentage=50)
                assert FeatureFlagRepository.is_enabled_for(flag, uid) is False
                return
        pytest.fail("Could not find a user outside rollout in 1000 attempts")

    def test_no_user_id_partial_rollout_returns_false(self):
        flag = _flag(enabled=True, rollout_percentage=50, allowed_user_ids=[])
        assert FeatureFlagRepository.is_enabled_for(flag, None) is False

    def test_no_user_id_full_rollout_returns_true(self):
        flag = _flag(enabled=True, rollout_percentage=100, allowed_user_ids=[])
        assert FeatureFlagRepository.is_enabled_for(flag, None) is True
