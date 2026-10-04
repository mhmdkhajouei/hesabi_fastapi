import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import (
    Budget,
    Category,
    Household,
    HouseholdMember,
    HouseholdRole,
    User,
)
from app.security import create_access_token, hash_password


@pytest.fixture
async def category_test_env(db_session: AsyncSession) -> dict:
    owner = User(
        email="cat_owner@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Category Owner",
        is_active=True,
    )
    member = User(
        email="cat_member@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Category Member",
        is_active=True,
    )
    viewer = User(
        email="cat_viewer@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Category Viewer",
        is_active=True,
    )
    db_session.add_all([owner, member, viewer])
    await db_session.commit()
    await db_session.refresh(owner)
    await db_session.refresh(member)
    await db_session.refresh(viewer)

    household_primary = Household(name="Primary Household")
    household_secondary = Household(name="Secondary Household")
    db_session.add_all([household_primary, household_secondary])
    await db_session.commit()
    await db_session.refresh(household_primary)
    await db_session.refresh(household_secondary)

    db_session.add_all(
        [
            HouseholdMember(
                user_id=owner.id,
                household_id=household_primary.id,
                role=HouseholdRole.OWNER,
            ),
            HouseholdMember(
                user_id=member.id,
                household_id=household_primary.id,
                role=HouseholdRole.MEMBER,
            ),
            HouseholdMember(
                user_id=viewer.id,
                household_id=household_primary.id,
                role=HouseholdRole.VIEWER,
            ),
        ]
    )
    await db_session.commit()

    return {
        "owner_token": create_access_token(subject=str(owner.id)),
        "member_token": create_access_token(subject=str(member.id)),
        "viewer_token": create_access_token(subject=str(viewer.id)),
        "household_id": household_primary.id,
        "foreign_household_id": household_secondary.id,
    }


@pytest.fixture
async def existing_category(
    db_session: AsyncSession, category_test_env: dict
) -> Category:
    category = Category(
        name="Groceries",
        budget=Budget(goal=5000000),
        household_id=category_test_env["household_id"],
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.mark.asyncio
class TestCategoryEndpoints:
    async def test_create_category_happy_path(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        category_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['owner_token']}"}
        payload = {"name": "Healthcare", "budget_goal": 3000000}

        response = await async_client.post(
            f"/api/v1/households/{category_test_env['household_id']}/categories/",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == payload["name"]
        assert data["budget_goal"] == payload["budget_goal"]

        query = (
            select(Category)
            .options(selectinload(Category.budget))
            .where(Category.id == data["id"])
        )

        result = await db_session.execute(query)
        category_in_db = result.scalar_one_or_none()
        assert category_in_db is not None
        assert category_in_db.name == payload["name"]
        assert category_in_db.budget.goal == payload["budget_goal"]
        assert category_in_db.household_id == category_test_env["household_id"]

    async def test_create_category_name_strip_whitespace(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        category_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['owner_token']}"}
        payload = {"name": "   Education   ", "budget_goal": 1500000}

        response = await async_client.post(
            f"/api/v1/households/{category_test_env['household_id']}/categories/",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Education"

        query = select(Category).where(Category.id == data["id"])
        result = await db_session.execute(query)
        category_in_db = result.scalar_one()
        assert category_in_db.name == "Education"

    @pytest.mark.parametrize(
        "name,goal",
        [
            ("A", 1),
            ("A" * 20, 100000000),
        ],
    )
    async def test_create_category_boundary_values(
        self,
        async_client: AsyncClient,
        category_test_env: dict,
        name: str,
        goal: int,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['owner_token']}"}
        payload = {"name": name, "budget_goal": goal}

        response = await async_client.post(
            f"/api/v1/households/{category_test_env['household_id']}/categories/",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == name
        assert data["budget_goal"] == goal

    @pytest.mark.parametrize(
        "role_key",
        ["member_token", "viewer_token"],
    )
    async def test_create_category_non_owner_forbidden(
        self,
        async_client: AsyncClient,
        category_test_env: dict,
        role_key: str,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env[role_key]}"}
        payload = {"name": "Travel", "budget_goal": 2000000}

        response = await async_client.post(
            f"/api/v1/households/{category_test_env['household_id']}/categories/",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INSUFFICIENT_PERMISSIONS"

    async def test_create_category_unauthorized(
        self,
        async_client: AsyncClient,
        category_test_env: dict,
    ) -> None:
        payload = {"name": "Travel", "budget_goal": 2000000}

        response = await async_client.post(
            f"/api/v1/households/{category_test_env['household_id']}/categories/",
            json=payload,
        )

        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Bearer"

    @pytest.mark.parametrize(
        "invalid_payload",
        [
            {"name": "", "budget_goal": 500000},
            {"name": "   ", "budget_goal": 500000},
            {"name": "A" * 21, "budget_goal": 500000},
            {"name": "Valid", "budget_goal": 0},
            {"name": "Valid", "budget_goal": -1},
            {"name": "Valid"},
            {"budget_goal": 500000},
        ],
    )
    async def test_create_category_payload_validation_errors(
        self,
        async_client: AsyncClient,
        category_test_env: dict,
        invalid_payload: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['owner_token']}"}

        response = await async_client.post(
            f"/api/v1/households/{category_test_env['household_id']}/categories/",
            json=invalid_payload,
            headers=headers,
        )

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "VALIDATION_ERROR"
        assert data["message"] == "Invalid request payload or query parameters"
        assert isinstance(data["errors"], list)
        assert len(data["errors"]) > 0

    @pytest.mark.parametrize("invalid_household_id", [0, -1])
    async def test_create_category_invalid_path_parameter(
        self,
        async_client: AsyncClient,
        category_test_env: dict,
        invalid_household_id: int,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['owner_token']}"}
        payload = {"name": "Valid", "budget_goal": 500000}

        response = await async_client.post(
            f"/api/v1/households/{invalid_household_id}/categories/",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "VALIDATION_ERROR"

    async def test_get_category_by_id_happy_path(
        self,
        async_client: AsyncClient,
        category_test_env: dict,
        existing_category: Category,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['viewer_token']}"}

        response = await async_client.get(
            f"/api/v1/households/{category_test_env['household_id']}/categories/{existing_category.id}",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == existing_category.id
        assert data["name"] == existing_category.name
        assert data["budget_goal"] == existing_category.budget_goal

    async def test_get_category_not_found(
        self,
        async_client: AsyncClient,
        category_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['owner_token']}"}

        response = await async_client.get(
            f"/api/v1/households/{category_test_env['household_id']}/categories/999999",
            headers=headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "CATEGORY_NOT_FOUND"
        assert data["message"] == "Category with ID 999999 not found"

    async def test_get_category_cross_household_bola_protection(
        self,
        async_client: AsyncClient,
        category_test_env: dict,
        existing_category: Category,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['owner_token']}"}

        response = await async_client.get(
            f"/api/v1/households/{category_test_env['foreign_household_id']}/categories/{existing_category.id}",
            headers=headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "HOUSEHOLD_NOT_FOUND"

    async def test_get_all_categories_happy_path(
        self,
        async_client: AsyncClient,
        category_test_env: dict,
        existing_category: Category,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['member_token']}"}

        response = await async_client.get(
            f"/api/v1/households/{category_test_env['household_id']}/categories/",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(item["id"] == existing_category.id for item in data)

    async def test_patch_category_partial_fields(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        category_test_env: dict,
        existing_category: Category,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['owner_token']}"}

        response_name = await async_client.patch(
            f"/api/v1/households/{category_test_env['household_id']}/categories/{existing_category.id}",
            json={"name": "Supermarket"},
            headers=headers,
        )
        assert response_name.status_code == 200
        assert response_name.json()["name"] == "Supermarket"
        assert response_name.json()["budget_goal"] == existing_category.budget_goal

        response_goal = await async_client.patch(
            f"/api/v1/households/{category_test_env['household_id']}/categories/{existing_category.id}",
            json={"budget_goal": 8000000},
            headers=headers,
        )
        assert response_goal.status_code == 200
        assert response_goal.json()["name"] == "Supermarket"
        assert response_goal.json()["budget_goal"] == 8000000

        query = select(Category).where(Category.id == existing_category.id)
        result = await db_session.execute(query)
        category_in_db = result.scalar_one()
        assert category_in_db.name == "Supermarket"
        assert category_in_db.budget_goal == 8000000

    async def test_patch_category_empty_payload_noop(
        self,
        async_client: AsyncClient,
        category_test_env: dict,
        existing_category: Category,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['owner_token']}"}

        response = await async_client.patch(
            f"/api/v1/households/{category_test_env['household_id']}/categories/{existing_category.id}",
            json={},
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == existing_category.name
        assert data["budget_goal"] == existing_category.budget_goal

    async def test_patch_category_not_found(
        self,
        async_client: AsyncClient,
        category_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['owner_token']}"}

        response = await async_client.patch(
            f"/api/v1/households/{category_test_env['household_id']}/categories/999999",
            json={"name": "New"},
            headers=headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "CATEGORY_NOT_FOUND"

    async def test_delete_category_happy_path(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        category_test_env: dict,
        existing_category: Category,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['owner_token']}"}

        response = await async_client.delete(
            f"/api/v1/households/{category_test_env['household_id']}/categories/{existing_category.id}",
            headers=headers,
        )

        assert response.status_code == 204
        assert response.content == b""

        query = select(Category).where(Category.id == existing_category.id)
        result = await db_session.execute(query)
        assert result.scalar_one_or_none() is None

    async def test_delete_category_not_found(
        self,
        async_client: AsyncClient,
        category_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['owner_token']}"}

        response = await async_client.delete(
            f"/api/v1/households/{category_test_env['household_id']}/categories/999999",
            headers=headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "CATEGORY_NOT_FOUND"
        assert data["message"] == "Category with ID 999999 not found"

    async def test_delete_category_non_owner_forbidden(
        self,
        async_client: AsyncClient,
        category_test_env: dict,
        existing_category: Category,
    ) -> None:
        headers = {"Authorization": f"Bearer {category_test_env['member_token']}"}

        response = await async_client.delete(
            f"/api/v1/households/{category_test_env['household_id']}/categories/{existing_category.id}",
            headers=headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INSUFFICIENT_PERMISSIONS"
