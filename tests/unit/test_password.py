import pytest

from app.core.security.hash_lib import hash_password, verify_password


@pytest.mark.unit
class TestHashPassword:
    def test_returns_non_empty_string(self):
        hashed = hash_password("Testpass1!")
        assert isinstance(hashed, str) and len(hashed) > 0

    def test_different_hash_each_call(self):
        h1 = hash_password("Testpass1!")
        h2 = hash_password("Testpass1!")
        assert h1 != h2  # argon2 adds salt

    def test_does_not_store_plaintext(self):
        hashed = hash_password("Testpass1!")
        assert "Testpass1!" not in hashed


@pytest.mark.unit
class TestVerifyPassword:
    def test_correct_password_returns_valid(self):
        hashed = hash_password("Correct1!")
        is_valid, _ = verify_password("Correct1!", hashed)
        assert is_valid is True

    def test_wrong_password_returns_invalid(self):
        hashed = hash_password("Correct1!")
        is_valid, _ = verify_password("Wrong1!", hashed)
        assert is_valid is False

    def test_returns_need_rehash_flag(self):
        hashed = hash_password("Testpass1!")
        _, need_rehash = verify_password("Testpass1!", hashed)
        assert isinstance(need_rehash, bool)
