import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/auth/me"


class TestAuthMeValidation:
    async def test_get_needs_no_body_200(self, user_client):
        assert (await user_client.get(BASE)).status_code == 200

    async def test_extra_query_params_ignored(self, user_client):
        assert (await user_client.get(BASE, params={"foo": "bar"})).status_code == 200
