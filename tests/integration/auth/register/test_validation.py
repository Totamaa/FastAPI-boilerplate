import pytest

from tests.integration.builders import user_payload

pytestmark = pytest.mark.integration
BASE = "/api/v1/auth/register"


class TestRegisterValidation:
    async def test_missing_email_422(self, client):
        p = {k: v for k, v in user_payload().items() if k != "email"}
        assert (await client.post(BASE, json=p)).status_code == 422

    async def test_invalid_email_format_422(self, client):
        assert (await client.post(BASE, json=user_payload(email="not-an-email"))).status_code == 422

    async def test_email_too_long_422(self, client):
        assert (
            await client.post(BASE, json=user_payload(email="a" * 250 + "@x.com"))
        ).status_code == 422

    async def test_missing_password_422(self, client):
        p = {k: v for k, v in user_payload().items() if k != "password"}
        assert (await client.post(BASE, json=p)).status_code == 422

    async def test_password_too_short_422(self, client):
        assert (
            await client.post(BASE, json=user_payload(password="Ab1!", password_confirm="Ab1!"))
        ).status_code == 422

    async def test_password_too_long_422(self, client):
        pw = "A1!" + "a" * 126
        assert (
            await client.post(BASE, json=user_payload(password=pw, password_confirm=pw))
        ).status_code == 422

    async def test_password_no_uppercase_422(self, client):
        assert (
            await client.post(
                BASE, json=user_payload(password="testpass1!", password_confirm="testpass1!")
            )
        ).status_code == 422

    async def test_password_no_lowercase_422(self, client):
        assert (
            await client.post(
                BASE, json=user_payload(password="TESTPASS1!", password_confirm="TESTPASS1!")
            )
        ).status_code == 422

    async def test_password_no_digit_422(self, client):
        assert (
            await client.post(
                BASE, json=user_payload(password="Testpasswd!", password_confirm="Testpasswd!")
            )
        ).status_code == 422

    async def test_password_no_special_422(self, client):
        assert (
            await client.post(
                BASE, json=user_payload(password="Testpass123", password_confirm="Testpass123")
            )
        ).status_code == 422

    async def test_passwords_mismatch_422(self, client):
        assert (
            await client.post(BASE, json=user_payload(password_confirm="Different1!"))
        ).status_code == 422

    async def test_missing_password_confirm_422(self, client):
        p = {k: v for k, v in user_payload().items() if k != "password_confirm"}
        assert (await client.post(BASE, json=p)).status_code == 422

    async def test_empty_body_422(self, client):
        assert (await client.post(BASE, json={})).status_code == 422
