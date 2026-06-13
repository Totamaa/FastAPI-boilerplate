import time

import redis.asyncio as aioredis
from sqlalchemy import text

from app.core.config.database import engine
from app.core.config.redis import REDIS_URL


async def check_db() -> dict:
    start = time.monotonic()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        return {"status": "ok", "latency_ms": latency_ms}
    except Exception as exc:
        return {"status": "down", "error": str(exc)}


async def check_redis() -> dict:
    start = time.monotonic()
    client: aioredis.Redis | None = None
    try:
        client = aioredis.from_url(REDIS_URL)
        await client.ping()
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        return {"status": "ok", "latency_ms": latency_ms}
    except Exception as exc:
        return {"status": "down", "error": str(exc)}
    finally:
        if client is not None:
            await client.aclose()


def compute_overall_status(checks: dict[str, dict]) -> str:
    db_status = checks.get("db", {}).get("status", "down")
    redis_status = checks.get("redis", {}).get("status", "down")

    if db_status == "down":
        return "down"
    if redis_status == "down":
        return "degraded"
    return "ok"
