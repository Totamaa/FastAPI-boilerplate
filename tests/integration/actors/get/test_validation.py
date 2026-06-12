import pytest

from tests.integration.builders import INVALID_UUID

pytestmark = pytest.mark.integration
BASE = "/api/v1/actors"


class TestActorsGetValidation:
    async def test_invalid_uuid_422(self, client):
        assert (await client.get(f"{BASE}/{INVALID_UUID}")).status_code == 422

    async def test_extra_query_params_ignored(self, client, test_actor):
        assert (
            await client.get(f"{BASE}/{test_actor.id}", params={"foo": "bar"})
        ).status_code == 200
