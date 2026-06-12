import pytest

from tests.integration.builders import NONEXISTENT_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/directors"


class TestDirectorsMoviesErrors:
    async def test_nonexistent_director_404(self, client):
        assert (await client.get(f"{BASE}/{NONEXISTENT_UUID}/movies")).status_code == 404
