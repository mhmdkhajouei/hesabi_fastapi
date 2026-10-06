from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import (
    Budget,
    Category,
    Household,
    HouseholdMember,
    HouseholdRole,
    Transaction,
    User,
)
from app.security import create_access_token, hash_password


@pytest.fixture
async def compute_test_env(db_session: AsyncSession) -> dict:
    user = User(
        email="compute_lead@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Compute Lead",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    household_active = Household(name="Active Compute Household")
    household_empty = Household(name="Empty Compute Household")
    db_session.add_all([household_active, household_empty])
    await db_session.commit()
    await db_session.refresh(household_active)
    await db_session.refresh(household_empty)

    db_session.add_all(
        [
            HouseholdMember(
                user_id=user.id,
                household_id=household_active.id,
                role=HouseholdRole.OWNER,
            ),
            HouseholdMember(
                user_id=user.id,
                household_id=household_empty.id,
                role=HouseholdRole.OWNER,
            ),
        ]
    )

    food_cat = Category(
        name="Food",
        budget=Budget(goal=1000000),
        household_id=household_active.id,
    )
    rent_cat = Category(
        name="Rent",
        budget=Budget(goal=5000000),
        household_id=household_active.id,
    )
    entertainment_cat = Category(
        name="Entertainment",
        budget=Budget(goal=500000),
        household_id=household_active.id,
    )
    db_session.add_all([food_cat, rent_cat, entertainment_cat])
    await db_session.commit()
    await db_session.refresh(food_cat)
    await db_session.refresh(rent_cat)
    await db_session.refresh(entertainment_cat)

    db_session.add_all(
        [
            Transaction(
                amount=8000000,
                type="income",
                household_id=household_active.id,
                created_by=user.id,
                category_id=None,
                date=datetime.now(UTC),
            ),
            Transaction(
                amount=2000000,
                type="income",
                household_id=household_active.id,
                created_by=user.id,
                category_id=None,
                date=datetime.now(UTC),
            ),
            Transaction(
                amount=600000,
                type="expense",
                household_id=household_active.id,
                created_by=user.id,
                category_id=food_cat.id,
                date=datetime.now(UTC),
            ),
            Transaction(
                amount=400000,
                type="expense",
                household_id=household_active.id,
                created_by=user.id,
                category_id=food_cat.id,
                date=datetime.now(UTC),
            ),
            Transaction(
                amount=700000,
                type="expense",
                household_id=household_active.id,
                created_by=user.id,
                category_id=entertainment_cat.id,
                date=datetime.now(UTC),
            ),
        ]
    )
    await db_session.commit()

    return {
        "token": create_access_token(subject=str(user.id)),
        "household_id": household_active.id,
        "empty_household_id": household_empty.id,
        "food_cat_id": food_cat.id,
        "rent_cat_id": rent_cat.id,
        "entertainment_cat_id": entertainment_cat.id,
    }


@pytest.mark.asyncio
class TestComputeEndpoints:
    async def test_get_summary_happy_path(
        self,
        async_client: AsyncClient,
        compute_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {compute_test_env['token']}"}

        response = await async_client.get(
            f"/api/v1/households/{compute_test_env['household_id']}/compute/summary",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["income"] == 10000000
        assert data["expense"] == 1700000
        assert data["total"] == 8300000
        assert data["currency"] == "TOMAN"

    async def test_get_summary_empty_household_zero_state(
        self,
        async_client: AsyncClient,
        compute_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {compute_test_env['token']}"}

        response = await async_client.get(
            f"/api/v1/households/{compute_test_env['empty_household_id']}/compute/summary",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["income"] == 0
        assert data["expense"] == 0
        assert data["total"] == 0
        assert data["currency"] == "TOMAN"

    async def test_get_category_balance_utilized(
        self,
        async_client: AsyncClient,
        compute_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {compute_test_env['token']}"}

        response = await async_client.get(
            f"/api/v1/households/{compute_test_env['household_id']}/compute/{compute_test_env['food_cat_id']}",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Food"
        assert data["budget_goal"] == 1000000
        assert data["spent"] == 1000000
        assert data["remaining"] == 0

    async def test_get_category_balance_unused_zero_expenses(
        self,
        async_client: AsyncClient,
        compute_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {compute_test_env['token']}"}

        response = await async_client.get(
            f"/api/v1/households/{compute_test_env['household_id']}/compute/{compute_test_env['rent_cat_id']}",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Rent"
        assert data["budget_goal"] == 5000000
        assert data["spent"] == 0
        assert data["remaining"] == 5000000

    async def test_get_category_balance_over_budget_negative_remaining(
        self,
        async_client: AsyncClient,
        compute_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {compute_test_env['token']}"}

        response = await async_client.get(
            f"/api/v1/households/{compute_test_env['household_id']}/compute/{compute_test_env['entertainment_cat_id']}",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Entertainment"
        assert data["budget_goal"] == 500000
        assert data["spent"] == 700000
        assert data["remaining"] == -200000

    async def test_get_category_balance_not_found(
        self,
        async_client: AsyncClient,
        compute_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {compute_test_env['token']}"}

        response = await async_client.get(
            f"/api/v1/households/{compute_test_env['household_id']}/compute/999999",
            headers=headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "CATEGORY_NOT_FOUND"
        assert data["message"] == "Category with ID 999999 not found"

    async def test_get_all_categories_balance_happy_path(
        self,
        async_client: AsyncClient,
        compute_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {compute_test_env['token']}"}

        response = await async_client.get(
            f"/api/v1/households/{compute_test_env['household_id']}/compute/categories",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

        food_stat = next(c for c in data if c["name"] == "Food")
        assert food_stat["spent"] == 1000000
        assert food_stat["remaining"] == 0

        rent_stat = next(c for c in data if c["name"] == "Rent")
        assert rent_stat["spent"] == 0
        assert rent_stat["remaining"] == 5000000

    async def test_get_all_categories_balance_empty_household(
        self,
        async_client: AsyncClient,
        compute_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {compute_test_env['token']}"}

        response = await async_client.get(
            f"/api/v1/households/{compute_test_env['empty_household_id']}/compute/categories",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.parametrize("invalid_household_id", [0, -5])
    async def test_compute_path_household_id_validation_error(
        self,
        async_client: AsyncClient,
        compute_test_env: dict,
        invalid_household_id: int,
    ) -> None:
        headers = {"Authorization": f"Bearer {compute_test_env['token']}"}

        response = await async_client.get(
            f"/api/v1/households/{invalid_household_id}/compute/summary",
            headers=headers,
        )

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "VALIDATION_ERROR"
        assert len(data["errors"]) > 0

    @pytest.mark.parametrize("invalid_category_id", [0, -1])
    async def test_compute_path_category_id_validation_error(
        self,
        async_client: AsyncClient,
        compute_test_env: dict,
        invalid_category_id: int,
    ) -> None:
        headers = {"Authorization": f"Bearer {compute_test_env['token']}"}

        response = await async_client.get(
            f"/api/v1/households/{compute_test_env['household_id']}/compute/{invalid_category_id}",
            headers=headers,
        )

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "VALIDATION_ERROR"

    async def test_compute_unauthorized_missing_token(
        self,
        async_client: AsyncClient,
        compute_test_env: dict,
    ) -> None:
        response = await async_client.get(
            f"/api/v1/households/{compute_test_env['household_id']}/compute/summary"
        )

        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Bearer"
