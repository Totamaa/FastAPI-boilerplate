import pytest

from tests.integration.builders import user_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/auth/register"


class TestRegisterErrors:
    async def test_duplicate_email_409(self, client):
        p = user_payload()
        await client.post(BASE, json=p)
        assert (await client.post(BASE, json=p)).status_code == 409

    async def test_duplicate_email_case_insensitive_409(self, client):
        p = user_payload()
        await client.post(BASE, json=p)
        assert (await client.post(BASE, json={**p, "email": p["email"].upper()})).status_code == 409
