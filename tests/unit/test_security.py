import time
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.config import settings
from app.errors.exceptions import AuthenticationError
from app.schemas import TokenPayload
from app.security import (
    DUMMY_PASSWORD_HASH,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


@pytest.fixture
def plain_password() -> str:
    return "ValidP@ssw0rd123!"


class TestPasswordHashing:
    def test_hash_password_returns_different_string(self, plain_password: str):
        hashed = hash_password(plain_password)
        assert hashed != plain_password
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_verify_password_correct(self, plain_password: str):
        hashed = hash_password(plain_password)
        assert verify_password(plain_password, hashed) is True

    def test_verify_password_incorrect(self, plain_password: str):
        hashed = hash_password(plain_password)
        assert verify_password("WrongPassword123!", hashed) is False

    def test_dummy_password_hash_constant_behavior(self):
        assert isinstance(DUMMY_PASSWORD_HASH, str)
        assert (
            verify_password("dummy_constant_password_value", DUMMY_PASSWORD_HASH)
            is True
        )
        assert verify_password("random_attempt", DUMMY_PASSWORD_HASH) is False


class TestJWTCreationAndDecoding:
    def test_create_access_token_claims(self):
        subject = "1"
        before = int(datetime.now(UTC).timestamp())
        token = create_access_token(subject=subject)
        after = int(datetime.now(UTC).timestamp())

        payload = decode_token(token)

        assert isinstance(payload, TokenPayload)
        assert payload.sub == subject
        assert payload.type == TokenType.ACCESS
        assert payload.iss == "hesabi-auth-service"
        assert payload.aud == "hesabi-client"
        assert before <= payload.iat <= after
        assert before <= payload.nbf <= after
        expected_exp = payload.iat + (settings.access_token_expire_minutes * 60)
        assert abs(payload.exp - expected_exp) <= 2

    def test_create_refresh_token_claims(self):
        subject = "2"
        token = create_refresh_token(subject=subject)

        payload = decode_token(token)

        assert isinstance(payload, TokenPayload)
        assert payload.sub == subject
        assert payload.type == TokenType.REFRESH
        assert payload.iss == "hesabi-auth-service"
        assert payload.aud == "hesabi-client"
        expected_exp = payload.iat + int(
            timedelta(days=settings.refresh_token_expire_days).total_seconds()
        )
        assert abs(payload.exp - expected_exp) <= 2

    def test_token_uniqueness(self):
        token_1 = create_access_token(subject="1")
        token_2 = create_access_token(subject="1")
        assert token_1 != token_2

    def test_decode_token_expired(self, monkeypatch):
        monkeypatch.setattr(settings, "access_token_expire_minutes", -1)
        token = create_access_token(subject="1")

        with pytest.raises(AuthenticationError) as exc_info:
            decode_token(token)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "TOKEN_EXPIRED"

    def test_decode_token_tampered_signature(self):
        token = create_access_token(subject="1")
        parts = token.split(".")
        tampered_token = f"{parts[0]}.{parts[1]}.invalid_signature"

        with pytest.raises(AuthenticationError) as exc_info:
            decode_token(tampered_token)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_TOKEN"

    def test_decode_token_invalid_issuer(self):
        now = int(time.time())
        payload = {
            "sub": "1",
            "exp": now + 3600,
            "iat": now,
            "nbf": now,
            "iss": "wrong-issuer",
            "aud": "hesabi-client",
            "jti": str(uuid4()),
            "type": TokenType.ACCESS,
        }
        token = jwt.encode(
            payload, settings.private_key, algorithm=settings.jwt_algorithm
        )

        with pytest.raises(AuthenticationError) as exc_info:
            decode_token(token)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_TOKEN"

    def test_decode_token_invalid_audience(self):
        now = int(time.time())
        payload = {
            "sub": "1",
            "exp": now + 3600,
            "iat": now,
            "nbf": now,
            "iss": "hesabi-auth-service",
            "aud": "wrong-client",
            "jti": str(uuid4()),
            "type": TokenType.ACCESS,
        }
        token = jwt.encode(
            payload, settings.private_key, algorithm=settings.jwt_algorithm
        )

        with pytest.raises(AuthenticationError) as exc_info:
            decode_token(token)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_TOKEN"

    @pytest.mark.parametrize(
        "missing_claim", ["sub", "exp", "iat", "nbf", "type", "iss", "aud"]
    )
    def test_decode_token_missing_required_claims(self, missing_claim: str):
        now = int(time.time())
        payload = {
            "sub": "1",
            "exp": now + 3600,
            "iat": now,
            "nbf": now,
            "iss": "hesabi-auth-service",
            "aud": "hesabi-client",
            "jti": str(uuid4()),
            "type": TokenType.ACCESS,
        }
        del payload[missing_claim]

        token = jwt.encode(
            payload, settings.private_key, algorithm=settings.jwt_algorithm
        )

        with pytest.raises(AuthenticationError) as exc_info:
            decode_token(token)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_TOKEN"

    def test_decode_token_signed_with_untrusted_private_key(self):
        foreign_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        foreign_pem = foreign_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        now = int(time.time())
        payload = {
            "sub": "1",
            "exp": now + 3600,
            "iat": now,
            "nbf": now,
            "iss": "hesabi-auth-service",
            "aud": "hesabi-client",
            "jti": str(uuid4()),
            "type": TokenType.ACCESS,
        }
        forged_token = jwt.encode(
            payload, foreign_pem, algorithm=settings.jwt_algorithm
        )

        with pytest.raises(AuthenticationError) as exc_info:
            decode_token(forged_token)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_TOKEN"

    def test_decode_malformed_token_string(self):
        with pytest.raises(AuthenticationError) as exc_info:
            decode_token("not.a.valid.jwt")

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_TOKEN"
