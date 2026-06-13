import pytest

pytestmark = pytest.mark.integration


class TestCacheControl:
    async def test_list_movies_short_cache(self, client, test_movie, settings):
        r = await client.get("/api/v1/movies")
        assert r.headers.get("cache-control") == f"public, max-age={settings.CACHE_MAX_AGE_SHORT}"

    async def test_get_movie_long_cache(self, client, test_movie, settings):
        r = await client.get(f"/api/v1/movies/{test_movie.id}")
        assert r.headers.get("cache-control") == f"public, max-age={settings.CACHE_MAX_AGE_LONG}"

    async def test_list_actors_short_cache(self, client, test_actor, settings):
        r = await client.get("/api/v1/actors")
        assert r.headers.get("cache-control") == f"public, max-age={settings.CACHE_MAX_AGE_SHORT}"

    async def test_list_genres_long_cache(self, client, test_genre, settings):
        r = await client.get("/api/v1/genres")
        assert r.headers.get("cache-control") == f"public, max-age={settings.CACHE_MAX_AGE_LONG}"

    async def test_no_cache_control_on_post(self, admin_client):
        from tests.integration.builders import movie_payload

        r = await admin_client.post("/api/v1/movies", json=movie_payload())
        assert "cache-control" not in r.headers
