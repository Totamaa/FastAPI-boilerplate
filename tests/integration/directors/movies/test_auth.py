import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"


class TestDirectorsMoviesAuth:
    async def test_public_no_auth(self, client, test_director):
        assert (await client.get(f"{BASE}/{test_director.id}/movies")).status_code == 200
