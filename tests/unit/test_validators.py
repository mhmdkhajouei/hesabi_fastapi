import pytest
from pydantic import BaseModel, ValidationError

from app.validators import (
    NormalizedEmail,
    StrongPassword,
    normalize_email_value,
    validate_password_complexity,
)


class DummyModel(BaseModel):
    email: NormalizedEmail
    password: StrongPassword


class TestNormalizeEmailValue:
    @pytest.mark.parametrize(
        "input_email, expected_output",
        [
            ("user@example.com", "user@example.com"),
            ("USER@EXAMPLE.COM", "user@example.com"),
            ("  user@example.com  ", "user@example.com"),
            ("\n\tUSER@EXAMPLE.COM \r\n", "user@example.com"),
            ("  User.Name+Tag@Sub.Domain.COM  ", "user.name+tag@sub.domain.com"),
        ],
    )
    def test_normalize_email_happy_and_edge_cases(self, input_email, expected_output):
        assert normalize_email_value(input_email) == expected_output

    def test_normalize_email_empty_string(self):
        assert normalize_email_value("") == ""
        assert normalize_email_value("   ") == ""

    @pytest.mark.parametrize(
        "non_string_value",
        [
            123,
            12.34,
            None,
            True,
            ["test@example.com"],
            {"email": "test@example.com"},
        ],
    )
    def test_normalize_email_non_string_passthrough(self, non_string_value):
        assert normalize_email_value(non_string_value) == non_string_value


class TestValidatePasswordComplexity:
    @pytest.mark.parametrize(
        "valid_password",
        [
            "Aa1",
            "StrongPass1",
            "1aA",
            "P@ssw0rd2026!",
            "123456789aA",
            "A" * 50 + "a" * 50 + "1" * 50,
            "Aa1!@#$%^&*()_+=-`~[]{}|;':\",./<>?",
            "Valid1 Password",
        ],
    )
    def test_validate_password_complexity_happy_and_boundaries(self, valid_password):
        assert validate_password_complexity(valid_password) == valid_password

    @pytest.mark.parametrize(
        "invalid_password",
        [
            "",
            "   ",
            "lowercase123",
            "UPPERCASE123",
            "UpperAndLowerOnly",
            "1234567890",
            "!@#$%^&*()_+",
            "UPPER!@#$",
            "lower!@#$",
            "12345!@#$",
        ],
    )
    def test_validate_password_complexity_raises_business_rule_error(
        self, invalid_password
    ):
        with pytest.raises(ValueError) as exc_info:
            validate_password_complexity(invalid_password)

        assert (
            "Password must contain at least one uppercase letter, one lowercase letter, and one number"
            in str(exc_info.value)
        )


class TestPydanticIntegrationTypes:
    def test_dummy_model_valid_inputs(self):
        instance = DummyModel(
            email="  Mohammad@Hesabi.Com  ",
            password="SecurePassword2026",
        )
        assert instance.email == "mohammad@hesabi.com"
        assert instance.password == "SecurePassword2026"

    @pytest.mark.parametrize(
        "invalid_email",
        [
            "not-an-email",
            "missing-domain@",
            "@missing-username.com",
            "spaces in email@domain.com",
            "",
        ],
    )
    def test_normalized_email_invalid_email_format(self, invalid_email):
        with pytest.raises(ValidationError):
            DummyModel(email=invalid_email, password="ValidPassword1")

    def test_strong_password_pydantic_wraps_error(self):
        with pytest.raises(ValidationError) as exc_info:
            DummyModel(email="valid@example.com", password="weakpassword")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("password",)
        assert (
            "Password must contain at least one uppercase letter, one lowercase letter, and one number"
            in errors[0]["msg"]
        )
