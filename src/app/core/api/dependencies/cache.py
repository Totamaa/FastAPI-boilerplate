from fastapi import Depends, Response

from app.core.config.settings import get_settings


def public_cache(max_age: int) -> Depends:
    async def _set(response: Response) -> None:
        response.headers["Cache-Control"] = f"public, max-age={max_age}"

    return Depends(_set)


def short_cache() -> Depends:
    return public_cache(get_settings().CACHE_MAX_AGE_SHORT)


def long_cache() -> Depends:
    return public_cache(get_settings().CACHE_MAX_AGE_LONG)
