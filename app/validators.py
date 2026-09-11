import re
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, EmailStr


def normalize_email_value(v: object) -> object:
    if isinstance(v, str):
        return v.strip().lower()
    return v


def validate_password_complexity(v: str) -> str:
    has_upper = bool(re.search(r"[A-Z]", v))
    has_lower = bool(re.search(r"[a-z]", v))
    has_digit = bool(re.search(r"\d", v))

    if not (has_upper and has_lower and has_digit):
        raise ValueError(
            "Password must contain at least one uppercase letter, one lowercase letter, and one number"
        )
    return v


NormalizedEmail = Annotated[EmailStr, BeforeValidator(normalize_email_value)]
StrongPassword = Annotated[str, AfterValidator(validate_password_complexity)]
