import pytest

from tests.integration.builders import NONEXISTENT_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesGetErrors:
    async def test_not_found_404(self, client):
        assert (await client.get(f"{BASE}/{NONEXISTENT_UUID}")).status_code == 404
