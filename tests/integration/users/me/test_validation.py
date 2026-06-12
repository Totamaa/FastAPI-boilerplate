import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/users/me"


class TestUsersMeValidation:
    async def test_no_body_needed(self, user_client):
        assert (await user_client.get(BASE)).status_code == 200

    async def test_extra_query_params_ignored(self, user_client):
        assert (await user_client.get(BASE, params={"extra": "param"})).status_code == 200
