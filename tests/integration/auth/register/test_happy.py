import pytest

pytestmark = pytest.mark.integration
BASE = "/api/v1/auth/register"
VALID = {"email": "new@example.com", "password": "Testpass1!", "password_confirm": "Testpass1!"}


class TestRegisterHappy:
    async def test_creates_user_returns_201(self, client):
        r = await client.post(BASE, json=VALID)
        assert r.status_code == 201

    async def test_response_has_user_fields(self, client):
        r = await client.post(BASE, json=VALID)
        d = r.json()
        assert d["email"] == VALID["email"]
        assert "id" in d and "is_active" in d and "created_at" in d

    async def test_password_not_in_response(self, client):
        r = await client.post(BASE, json=VALID)
        d = r.json()
        assert "password" not in d and "hashed_password" not in d

    async def test_new_user_active_not_admin(self, client):
        r = await client.post(BASE, json=VALID)
        d = r.json()
        assert d["is_active"] is True and d["is_admin"] is False

    async def test_extra_fields_ignored(self, client):
        r = await client.post(BASE, json={**VALID, "email": "x2@example.com", "role": "admin"})
        assert r.status_code == 201
