import pytest
from faker import Faker

pytestmark = pytest.mark.integration
BASE = "/api/v1/auth/login"
fake = Faker()


class TestLoginValidation:
    async def test_missing_username_422(self, client):
        assert (await client.post(BASE, data={"password": "Testpass1!"})).status_code == 422

    async def test_missing_password_422(self, client):
        assert (await client.post(BASE, data={"username": fake.email()})).status_code == 422

    async def test_empty_body_422(self, client):
        assert (await client.post(BASE, data={})).status_code == 422

    async def test_json_body_not_accepted_422(self, client):
        assert (
            await client.post(BASE, json={"username": fake.email(), "password": "Testpass1!"})
        ).status_code == 422
