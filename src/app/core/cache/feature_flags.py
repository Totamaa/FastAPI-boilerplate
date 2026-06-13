import contextlib
import json
from typing import Any

import redis.asyncio as aioredis

from app.core.config.redis import REDIS_URL
from app.core.config.settings import get_settings

_CACHE_KEY = "flags:all"
_redis: aioredis.Redis | None = None


def _get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


def _ttl() -> int:
    return get_settings().CACHE_MAX_AGE_SHORT


async def get_all_cached() -> list[dict] | None:
    try:
        raw = await _get_redis().get(_CACHE_KEY)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception:
        return None


async def set_all_cached(flags: list[dict[str, Any]]) -> None:
    with contextlib.suppress(Exception):
        await _get_redis().setex(_CACHE_KEY, _ttl(), json.dumps(flags, default=str))


async def invalidate() -> None:
    with contextlib.suppress(Exception):
        await _get_redis().delete(_CACHE_KEY)
