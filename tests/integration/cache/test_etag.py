import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestEtag:
    async def test_etag_header_present_on_get(self, client, test_movie):
        r = await client.get(BASE)
        assert "etag" in r.headers

    async def test_same_response_yields_same_etag(self, client, test_movie):
        r1 = await client.get(BASE)
        r2 = await client.get(BASE)
        assert r1.headers["etag"] == r2.headers["etag"]

    async def test_304_on_matching_if_none_match(self, client, test_movie):
        r = await client.get(BASE)
        r2 = await client.get(BASE, headers={"If-None-Match": r.headers["etag"]})
        assert r2.status_code == 304

    async def test_304_has_no_body(self, client, test_movie):
        r = await client.get(BASE)
        r2 = await client.get(BASE, headers={"If-None-Match": r.headers["etag"]})
        assert r2.content == b""

    async def test_stale_etag_returns_200(self, client, test_movie):
        r = await client.get(BASE, headers={"If-None-Match": '"stale-etag-value"'})
        assert r.status_code == 200
        assert "etag" in r.headers

    async def test_etag_changes_after_update(self, client, admin_client, test_movie):
        r1 = await client.get(f"{BASE}/{test_movie.id}")
        etag1 = r1.headers["etag"]
        await admin_client.put(f"{BASE}/{test_movie.id}", json={"title": "Updated Title"})
        r2 = await client.get(f"{BASE}/{test_movie.id}")
        assert r2.headers["etag"] != etag1

    async def test_no_etag_on_201(self, admin_client):
        from tests.integration.builders import movie_payload

        r = await admin_client.post(BASE, json=movie_payload())
        assert r.status_code == 201
        assert "etag" not in r.headers

    async def test_no_etag_on_204(self, admin_client, test_movie):
        r = await admin_client.delete(f"{BASE}/{test_movie.id}")
        assert r.status_code == 204
        assert "etag" not in r.headers
