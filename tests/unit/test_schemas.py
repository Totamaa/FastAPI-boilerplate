import pytest
from pydantic import ValidationError

from app.modules.users.schemas import UserRegister


@pytest.mark.unit
class TestUserRegisterValidation:
    def test_valid_payload_passes(self):
        schema = UserRegister(
            email="user@example.com",
            password="Validpass1!",
            password_confirm="Validpass1!",
        )
        assert schema.email == "user@example.com"

    def test_missing_uppercase_raises(self):
        with pytest.raises(ValidationError, match="uppercase"):
            UserRegister(
                email="u@e.com", password="nouppercase1!", password_confirm="nouppercase1!"
            )

    def test_missing_lowercase_raises(self):
        with pytest.raises(ValidationError, match="lowercase"):
            UserRegister(email="u@e.com", password="NOLOWER1!", password_confirm="NOLOWER1!")

    def test_missing_digit_raises(self):
        with pytest.raises(ValidationError, match="digit"):
            UserRegister(email="u@e.com", password="NoDigitPass!", password_confirm="NoDigitPass!")

    def test_missing_special_char_raises(self):
        with pytest.raises(ValidationError, match="special"):
            UserRegister(email="u@e.com", password="NoSpecial1", password_confirm="NoSpecial1")

    def test_password_too_short_raises(self):
        with pytest.raises(ValidationError):
            UserRegister(email="u@e.com", password="Sh1!", password_confirm="Sh1!")

    def test_passwords_mismatch_raises(self):
        with pytest.raises(ValidationError, match="do not match"):
            UserRegister(
                email="u@e.com",
                password="Validpass1!",
                password_confirm="Different1!",
            )

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            UserRegister(
                email="not-an-email", password="Validpass1!", password_confirm="Validpass1!"
            )
