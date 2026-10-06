import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import User
from app.security import create_access_token, hash_password


@pytest.fixture
async def active_user(db_session: AsyncSession) -> dict:
    raw_password = "StrongPassword123!"
    user = User(
        email="active_user@example.com",
        password_hash=hash_password(raw_password),
        name="Active User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "raw_password": raw_password,
    }


@pytest.fixture
async def deactivated_user(db_session: AsyncSession) -> dict:
    raw_password = "StrongPassword123!"
    user = User(
        email="inactive_user@example.com",
        password_hash=hash_password(raw_password),
        name="Inactive User",
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "raw_password": raw_password,
    }


@pytest.mark.asyncio
class TestAuthEndpoints:
    async def test_register_happy_path_with_full_details(
        self, async_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        payload = {
            "email": "register_full@example.com",
            "name": "Full Name User",
            "password": "StrongPassword123!",
        }

        response = await async_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == payload["email"]
        assert data["name"] == payload["name"]
        assert data["is_active"] is True
        assert "password" not in data
        assert "password_hash" not in data

        query = select(User).where(User.email == payload["email"])
        result = await db_session.execute(query)
        user_in_db = result.scalar_one_or_none()

        assert user_in_db is not None
        assert user_in_db.name == payload["name"]
        assert user_in_db.password_hash != payload["password"]
        assert user_in_db.is_active is True

    async def test_register_happy_path_optional_name_omitted(
        self, async_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        payload = {
            "email": "register_no_name@example.com",
            "password": "StrongPassword123!",
        }

        response = await async_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] is None
        assert data["email"] == payload["email"]

        query = select(User).where(User.email == payload["email"])
        result = await db_session.execute(query)
        user_in_db = result.scalar_one_or_none()
        assert user_in_db is not None
        assert user_in_db.name is None

    async def test_register_duplicate_email_conflict(
        self, async_client: AsyncClient, active_user: dict
    ) -> None:
        payload = {
            "email": active_user["email"],
            "name": "Duplicate Attempt",
            "password": "StrongPassword123!",
        }

        response = await async_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "EMAIL_ALREADY_EXISTS"
        assert data["message"] == "A user with this email already exists"

    async def test_register_email_normalization_and_whitespace_strip(
        self, async_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        payload = {
            "email": "  NORMALIZED.User@EXAMPLE.COM  ",
            "name": "   Trimmed Name   ",
            "password": "StrongPassword123!",
        }

        response = await async_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "normalized.user@example.com"
        assert data["name"] == "Trimmed Name"

        query = select(User).where(User.email == "normalized.user@example.com")
        result = await db_session.execute(query)
        user_in_db = result.scalar_one_or_none()
        assert user_in_db is not None
        assert user_in_db.name == "Trimmed Name"

    @pytest.mark.parametrize(
        "invalid_payload",
        [
            {"email": "not-an-email", "password": "StrongPassword123!"},
            {"email": "", "password": "StrongPassword123!"},
            {"email": "valid@example.com", "password": "short"},
            {"email": "valid@example.com", "password": "NoDigitsPassword!"},
            {"email": "valid@example.com", "password": "nouppercase123!"},
            {"email": "valid@example.com", "password": "NOLOWERCASE123!"},
            {"email": "valid@example.com", "password": "NoSpecialCharacter123"},
            {"name": "No Email", "password": "StrongPassword123!"},
            {"email": "valid@example.com", "name": "No Password"},
        ],
    )
    async def test_register_validation_errors(
        self, async_client: AsyncClient, invalid_payload: dict
    ) -> None:
        response = await async_client.post(
            "/api/v1/auth/register", json=invalid_payload
        )

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "VALIDATION_ERROR"
        assert data["message"] == "Invalid request payload or query parameters"
        assert isinstance(data["errors"], list)
        assert len(data["errors"]) > 0

    async def test_login_happy_path(
        self, async_client: AsyncClient, active_user: dict
    ) -> None:
        payload = {
            "email": active_user["email"],
            "password": active_user["raw_password"],
        }

        response = await async_client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"].lower() == "bearer"
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0

    async def test_login_case_insensitive_email(
        self, async_client: AsyncClient, active_user: dict
    ) -> None:
        payload = {
            "email": active_user["email"].upper(),
            "password": active_user["raw_password"],
        }

        response = await async_client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_login_wrong_password(
        self, async_client: AsyncClient, active_user: dict
    ) -> None:
        payload = {
            "email": active_user["email"],
            "password": "CompletelyWrongPassword123!",
        }

        response = await async_client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Bearer"
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INVALID_CREDENTIALS"
        assert data["message"] == "Invalid email or password"

    async def test_login_nonexistent_user(self, async_client: AsyncClient) -> None:
        payload = {
            "email": "nobody@example.com",
            "password": "StrongPassword123!",
        }

        response = await async_client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Bearer"
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INVALID_CREDENTIALS"
        assert data["message"] == "Invalid email or password"

    async def test_login_deactivated_user(
        self, async_client: AsyncClient, deactivated_user: dict
    ) -> None:
        payload = {
            "email": deactivated_user["email"],
            "password": deactivated_user["raw_password"],
        }

        response = await async_client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Bearer"
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "USER_DEACTIVATED"
        assert data["message"] == "User account is deactivated"

    async def test_refresh_token_happy_path(
        self, async_client: AsyncClient, active_user: dict
    ) -> None:
        login_payload = {
            "email": active_user["email"],
            "password": active_user["raw_password"],
        }
        login_response = await async_client.post(
            "/api/v1/auth/login", json=login_payload
        )
        refresh_token = login_response.json()["refresh_token"]

        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"].lower() == "bearer"
        assert len(data["access_token"]) > 0

    async def test_refresh_token_using_access_token_rejected(
        self, async_client: AsyncClient, active_user: dict
    ) -> None:
        access_token = create_access_token(subject=str(active_user["id"]))

        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": access_token}
        )

        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Bearer"
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INVALID_TOKEN_TYPE"
        assert data["message"] == "Invalid token type for refresh"

    async def test_refresh_token_malformed_string(
        self, async_client: AsyncClient
    ) -> None:
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "a" * 120},
        )

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "VALIDATION_ERROR"
        assert data["message"] == "Invalid request payload or query parameters"
        assert isinstance(data["errors"], list)
        assert len(data["errors"]) > 0

    async def test_refresh_token_tampered_signature(
        self, async_client: AsyncClient, active_user: dict
    ) -> None:
        login_payload = {
            "email": active_user["email"],
            "password": active_user["raw_password"],
        }
        login_response = await async_client.post(
            "/api/v1/auth/login", json=login_payload
        )
        parts = login_response.json()["refresh_token"].split(".")
        tampered_token = f"{parts[0]}.{parts[1]}.{parts[2][:-5]}AAAAA"

        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tampered_token}
        )

        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Bearer"
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INVALID_TOKEN"

    async def test_refresh_token_deactivated_user(
        self,
        async_client: AsyncClient,
        active_user: dict,
        db_session: AsyncSession,
    ) -> None:
        login_payload = {
            "email": active_user["email"],
            "password": active_user["raw_password"],
        }
        login_response = await async_client.post(
            "/api/v1/auth/login", json=login_payload
        )
        refresh_token = login_response.json()["refresh_token"]

        query = select(User).where(User.id == active_user["id"])
        result = await db_session.execute(query)
        user_in_db = result.scalar_one()
        user_in_db.is_active = False
        await db_session.commit()

        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Bearer"
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "USER_DEACTIVATED"
        assert data["message"] == "User account is deactivated"

    async def test_refresh_token_deleted_user(
        self,
        async_client: AsyncClient,
        active_user: dict,
        db_session: AsyncSession,
    ) -> None:
        login_payload = {
            "email": active_user["email"],
            "password": active_user["raw_password"],
        }
        login_response = await async_client.post(
            "/api/v1/auth/login", json=login_payload
        )
        refresh_token = login_response.json()["refresh_token"]

        query = select(User).where(User.id == active_user["id"])
        result = await db_session.execute(query)
        user_in_db = result.scalar_one()
        await db_session.delete(user_in_db)
        await db_session.commit()

        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Bearer"
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "USER_NOT_FOUND"
        assert data["message"] == "User not found"
