from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Literal
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from app.config import settings
from app.schemas import TokenPayload

PASSWORD_HASHER = PasswordHash.recommended()


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    BEARER = "bearer"


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    return PASSWORD_HASHER.verify(password, password_hash)


def hash_password(password: str) -> str:
    return PASSWORD_HASHER.hash(password)


DUMMY_PASSWORD_HASH: str = hash_password("dummy_constant_password_value")


def _create_token(
    subject: str,
    token_type: Literal[TokenType.ACCESS, TokenType.REFRESH],
    expire_delta: timedelta,
) -> str:

    now = datetime.now(UTC)
    expire = now + expire_delta

    payload = {
        "sub": subject,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "iss": "hesabi-auth-service",
        "aud": "hesabi-client",
        "jti": str(uuid4()),
        "type": token_type,
    }

    return jwt.encode(
        payload,
        settings.private_key,
        algorithm=settings.jwt_algorithm,
    )


def create_access_token(subject: str) -> str:
    return _create_token(
        subject=subject,
        token_type=TokenType.ACCESS,
        expire_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(subject: str) -> str:
    return _create_token(
        subject=subject,
        token_type=TokenType.REFRESH,
        expire_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str) -> TokenPayload:
    decoded = jwt.decode(
        token,
        settings.public_key,
        algorithms=[settings.jwt_algorithm],
        issuer="hesabi-auth-service",
        audience="hesabi-client",
        options={"require": ["sub", "exp", "iat", "nbf", "type", "iss", "aud"]},
    )
    return TokenPayload.model_validate(decoded)
