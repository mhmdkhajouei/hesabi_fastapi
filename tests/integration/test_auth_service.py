import pytest

import app.service as service_module
from app.db.database import User
from app.dependencies import get_auth_service, get_user_repo
from app.errors.exceptions import AuthenticationError
from app.schemas import Token, TokenRefreshRequest, TokenRefreshResponse, UserLogin
from app.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
)

RAW_PASS = "StrongPassword123!"


@pytest.fixture
def auth_service(db_session):
    repo = get_user_repo(db_session)
    service = get_auth_service(repo)
    return service


@pytest.fixture
async def seed_active_user(db_session) -> User:
    user = User(
        email="auth_active@hesabi.com",
        password_hash=hash_password(RAW_PASS),
        name="Auth Active User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def seed_deactived_user(db_session) -> User:
    user = User(
        email="auth_inactive@hesabi.com",
        password_hash=hash_password(RAW_PASS),
        name="Auth Inactive User",
        is_active=False,
    )
    db_session.add(user)
    await db_session.flush()
    return user


class TestAuthenticateUser:
    async def test_login_success_happy_path(self, auth_service, seed_active_user):
        user = UserLogin(
            email=seed_active_user.email,
            password=RAW_PASS,
        )
        result = await auth_service.authenticate_user(user)

        assert isinstance(result, Token)
        assert result.token_type.lower() == "bearer"
        assert result.access_token is not None
        assert result.refresh_token is not None

        access_payload = decode_token(result.access_token)
        refresh_payload = decode_token(result.refresh_token)

        assert access_payload.sub == str(seed_active_user.id)
        assert access_payload.type == TokenType.ACCESS
        assert refresh_payload.sub == str(seed_active_user.id)
        assert refresh_payload.type == TokenType.REFRESH

    async def test_login_failure_invalid_user(self, auth_service):
        user = UserLogin(email="ghost_user@hesabi.com", password=RAW_PASS)

        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.authenticate_user(user)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_CREDENTIALS"

    @pytest.mark.parametrize(
        "wrong_password",
        [
            "WrongPassword123!",
            "strongpassword123!",
            "StrongPassword123! ",
            " StrongPassword123! ",
            "",
        ],
    )
    async def test_login_failure_invalid_password(
        self, auth_service, seed_active_user, wrong_password
    ):
        user = UserLogin(
            email=seed_active_user.email,
            password=wrong_password,
        )
        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.authenticate_user(user)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_CREDENTIALS"

    async def test_login_failure_inactive_user(self, auth_service, seed_deactived_user):
        user = UserLogin(
            email=seed_deactived_user.email,
            password=RAW_PASS,
        )
        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.authenticate_user(user)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "USER_DEACTIVATED"

    async def test_timing_attack_resistance(self, auth_service, mocker):
        spy_verify = mocker.spy(service_module, "verify_password")

        user = UserLogin(email="notfound@hesabi.com", password="DummyPassword123!")
        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.authenticate_user(user)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_CREDENTIALS"
        assert exc_info.value.message == "Invalid email or password"
        assert spy_verify.call_count == 1


class TestRequestRefreshToken:
    async def test_refresh_token_success(self, auth_service, seed_active_user):
        valid_refresh = create_refresh_token(subject=str(seed_active_user.id))
        req = TokenRefreshRequest(refresh_token=valid_refresh)

        response = await auth_service.request_refresh_token(req)

        assert isinstance(response, TokenRefreshResponse)
        assert response.token_type.lower() == "bearer"
        assert response.access_token is not None

        new_payload = decode_token(response.access_token)

        assert new_payload.sub == str(seed_active_user.id)
        assert new_payload.type == TokenType.ACCESS

    async def test_refresh_token_invalid_type(self, auth_service, seed_active_user):
        access_token = create_access_token(subject=str(seed_active_user.id))
        req = TokenRefreshRequest(refresh_token=access_token)

        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.request_refresh_token(req)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_TOKEN_TYPE"

    async def test_refresh_token_invalid_sub(self, auth_service):
        refresh_token = create_refresh_token(subject="not_an_int_id")
        req = TokenRefreshRequest(refresh_token=refresh_token)

        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.request_refresh_token(req)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_TOKEN_SUBJECT"

    async def test_refresh_token_user_not_found(self, auth_service):
        refresh_token = create_refresh_token(subject=str(999999))
        req = TokenRefreshRequest(refresh_token=refresh_token)

        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.request_refresh_token(req)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "USER_NOT_FOUND"

    async def test_refresh_token_inactive_user(self, auth_service, seed_deactived_user):
        refresh_token = create_refresh_token(subject=str(seed_deactived_user.id))
        req = TokenRefreshRequest(refresh_token=refresh_token)

        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.request_refresh_token(req)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "USER_DEACTIVATED"

    async def test_refresh_token_tampered_signature(self, auth_service):
        valid_token = create_refresh_token(subject="1")
        header, payload, _ = valid_token.split(".")
        tempered_token = f"{header}.{payload}.invalid_signature_part_here_long_enough"
        req = TokenRefreshRequest(refresh_token=tempered_token)

        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.request_refresh_token(req)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_TOKEN"

    async def test_refresh_token_malformed_string(self, auth_service):
        req = TokenRefreshRequest(refresh_token=f"{'a' * 35}.{'b' * 35}.{'c' * 35}")

        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.request_refresh_token(req)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "INVALID_TOKEN"
