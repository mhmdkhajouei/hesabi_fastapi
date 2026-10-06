import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import Household, HouseholdMember, HouseholdRole, User
from app.security import create_access_token, create_refresh_token, hash_password


@pytest.fixture
async def users_test_env(db_session: AsyncSession) -> dict:
    active_user = User(
        email="me_active@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Active Profile User",
        is_active=True,
    )
    user_without_household = User(
        email="me_nohh@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="No Household User",
        is_active=True,
    )
    deactivated_user = User(
        email="me_inactive@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Inactive Profile User",
        is_active=False,
    )
    db_session.add_all([active_user, user_without_household, deactivated_user])
    await db_session.flush()

    household = Household(
        name="Personal Household",
        is_personal=True,
    )
    db_session.add(household)
    await db_session.flush()

    membership = HouseholdMember(
        user_id=active_user.id,
        household_id=household.id,
        role=HouseholdRole.OWNER,
    )
    db_session.add(membership)
    await db_session.flush()

    return {
        "active_user_id": active_user.id,
        "active_token": create_access_token(subject=str(active_user.id)),
        "active_email": active_user.email,
        "active_name": active_user.name,
        "household_id": household.id,
        "no_hh_token": create_access_token(subject=str(user_without_household.id)),
        "no_hh_email": user_without_household.email,
        "inactive_token": create_access_token(subject=str(deactivated_user.id)),
        "inactive_user_id": deactivated_user.id,
    }


@pytest.mark.asyncio
class TestUsersEndpoints:
    async def test_get_me_happy_path(
        self,
        async_client: AsyncClient,
        users_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {users_test_env['active_token']}"}

        response = await async_client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == users_test_env["active_user_id"]
        assert data["email"] == users_test_env["active_email"]
        assert data["name"] == users_test_env["active_name"]
        assert data["is_active"] is True
        assert data["personal_household_id"] == users_test_env["household_id"]
        assert "created_at" in data
        assert "password" not in data
        assert "password_hash" not in data

    async def test_get_me_user_without_household_returns_none_household_id(
        self,
        async_client: AsyncClient,
        users_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {users_test_env['no_hh_token']}"}

        response = await async_client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == users_test_env["no_hh_email"]
        assert data["personal_household_id"] is None

    async def test_get_me_unauthorized_missing_token(
        self,
        async_client: AsyncClient,
    ) -> None:
        response = await async_client.get("/api/v1/users/me")

        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Bearer"

    async def test_get_me_invalid_bearer_prefix(
        self,
        async_client: AsyncClient,
        users_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Token {users_test_env['active_token']}"}

        response = await async_client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Bearer"

    async def test_get_me_malformed_token_string(
        self,
        async_client: AsyncClient,
    ) -> None:
        headers = {"Authorization": "Bearer not-a-valid-token"}

        response = await async_client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INVALID_TOKEN"

    async def test_get_me_tampered_signature(
        self,
        async_client: AsyncClient,
        users_test_env: dict,
    ) -> None:
        parts = users_test_env["active_token"].split(".")
        tampered_token = f"{parts[0]}.{parts[1]}.{parts[2][:-5]}AAAAA"
        headers = {"Authorization": f"Bearer {tampered_token}"}

        response = await async_client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INVALID_TOKEN"

    async def test_get_me_using_refresh_token_rejected(
        self,
        async_client: AsyncClient,
        users_test_env: dict,
    ) -> None:
        refresh_token = create_refresh_token(
            subject=str(users_test_env["active_user_id"])
        )
        headers = {"Authorization": f"Bearer {refresh_token}"}

        response = await async_client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INVALID_TOKEN_TYPE"

    async def test_get_me_deactivated_user_rejected(
        self,
        async_client: AsyncClient,
        users_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {users_test_env['inactive_token']}"}

        response = await async_client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "USER_DEACTIVATED"

    async def test_get_me_deleted_user_not_found(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        users_test_env: dict,
    ) -> None:
        query = select(User).where(User.id == users_test_env["active_user_id"])
        result = await db_session.execute(query)
        user_in_db = result.scalar_one()
        await db_session.delete(user_in_db)
        await db_session.commit()

        headers = {"Authorization": f"Bearer {users_test_env['active_token']}"}

        response = await async_client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "USER_NOT_FOUND"

    async def test_get_me_token_with_non_digit_subject(
        self,
        async_client: AsyncClient,
    ) -> None:
        token = create_access_token(subject="invalid_sub_uuid_string")
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INVALID_TOKEN_SUBJECT"
