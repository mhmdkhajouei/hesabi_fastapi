from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from pydantic import TypeAdapter
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
from app.schemas import (
    CategoryBalanceResponse,
    CategoryResponse,
    FinancialSummaryResponse,
    Token,
    TokenRefreshResponse,
    TransactionResponse,
    UserResponse,
)
from app.security import create_access_token, hash_password


@pytest.fixture
async def contract_env(db_session: AsyncSession) -> dict:
    raw_password = "StrongPassword123!"
    user = User(
        email="contract_user@example.com",
        password_hash=hash_password(raw_password),
        name="Contract User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    household = Household(name="Contract Household", is_personal=True)
    db_session.add(household)
    await db_session.flush()

    membership = HouseholdMember(
        user_id=user.id,
        household_id=household.id,
        role=HouseholdRole.OWNER,
    )
    category = Category(
        name="Contract Cat",
        budget=Budget(goal=2000000),
        household_id=household.id,
    )
    db_session.add_all([membership, category])
    await db_session.flush()

    tx = Transaction(
        amount=150000,
        type="expense",
        category_id=category.id,
        household_id=household.id,
        created_by=user.id,
        date=datetime.now(UTC),
        note="Initial sample expense",
    )
    db_session.add(tx)
    await db_session.flush()

    return {
        "user_id": user.id,
        "email": user.email,
        "raw_password": raw_password,
        "token": create_access_token(subject=str(user.id)),
        "household_id": household.id,
        "category_id": category.id,
        "transaction_id": tx.id,
    }


@pytest.mark.asyncio
class TestApiContractSchemas:
    async def test_auth_register_contract(self, async_client: AsyncClient) -> None:
        payload = {
            "email": "new_contract_user@example.com",
            "name": "New Registered",
            "password": "StrongPassword123!",
        }
        response = await async_client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201
        validated = UserResponse.model_validate(response.json())
        assert validated.email == payload["email"]
        assert validated.name == payload["name"]

    async def test_auth_login_contract(
        self, async_client: AsyncClient, contract_env: dict
    ) -> None:
        payload = {
            "email": contract_env["email"],
            "password": contract_env["raw_password"],
        }
        response = await async_client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 200
        validated = Token.model_validate(response.json())
        assert validated.token_type.lower() == "bearer"
        assert len(validated.access_token) > 0
        assert len(validated.refresh_token) > 0

    async def test_auth_refresh_contract(
        self, async_client: AsyncClient, contract_env: dict
    ) -> None:
        login_res = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": contract_env["email"],
                "password": contract_env["raw_password"],
            },
        )
        refresh_token = login_res.json()["refresh_token"]

        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        validated = TokenRefreshResponse.model_validate(response.json())
        assert validated.token_type.lower() == "bearer"
        assert len(validated.access_token) > 0

    async def test_users_me_contract(
        self, async_client: AsyncClient, contract_env: dict
    ) -> None:
        headers = {"Authorization": f"Bearer {contract_env['token']}"}
        response = await async_client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
        validated = UserResponse.model_validate(response.json())
        assert validated.id == contract_env["user_id"]
        assert validated.email == contract_env["email"]
        assert validated.personal_household_id == contract_env["household_id"]

    async def test_category_create_contract(
        self, async_client: AsyncClient, contract_env: dict
    ) -> None:
        headers = {"Authorization": f"Bearer {contract_env['token']}"}
        payload = {"name": "New Contract", "budget_goal": 500000}
        response = await async_client.post(
            f"/api/v1/households/{contract_env['household_id']}/categories/",
            json=payload,
            headers=headers,
        )
        assert response.status_code == 201
        validated = CategoryResponse.model_validate(response.json())
        assert validated.name == payload["name"]
        assert validated.budget_goal == payload["budget_goal"]

    async def test_category_get_contract(
        self, async_client: AsyncClient, contract_env: dict
    ) -> None:
        headers = {"Authorization": f"Bearer {contract_env['token']}"}
        response = await async_client.get(
            f"/api/v1/households/{contract_env['household_id']}/categories/{contract_env['category_id']}",
            headers=headers,
        )
        assert response.status_code == 200
        validated = CategoryResponse.model_validate(response.json())
        assert validated.id == contract_env["category_id"]

    async def test_category_get_all_contract(
        self, async_client: AsyncClient, contract_env: dict
    ) -> None:
        headers = {"Authorization": f"Bearer {contract_env['token']}"}
        response = await async_client.get(
            f"/api/v1/households/{contract_env['household_id']}/categories/",
            headers=headers,
        )
        assert response.status_code == 200
        validated_list = TypeAdapter(list[CategoryResponse]).validate_python(
            response.json()
        )
        assert len(validated_list) >= 1
        assert any(c.id == contract_env["category_id"] for c in validated_list)

    async def test_category_patch_contract(
        self, async_client: AsyncClient, contract_env: dict
    ) -> None:
        headers = {"Authorization": f"Bearer {contract_env['token']}"}
        payload = {"name": "Updated Cat"}
        response = await async_client.patch(
            f"/api/v1/households/{contract_env['household_id']}/categories/{contract_env['category_id']}",
            json=payload,
            headers=headers,
        )
        assert response.status_code == 200
        validated = CategoryResponse.model_validate(response.json())
        assert validated.id == contract_env["category_id"]
        assert validated.name == payload["name"]

    async def test_transaction_create_contract(
        self, async_client: AsyncClient, contract_env: dict
    ) -> None:
        headers = {"Authorization": f"Bearer {contract_env['token']}"}
        payload = {
            "amount": 250000,
            "type": "expense",
            "category_id": contract_env["category_id"],
            "note": "Contract verify note",
        }
        response = await async_client.post(
            f"/api/v1/households/{contract_env['household_id']}/transactions/",
            json=payload,
            headers=headers,
        )
        assert response.status_code == 201
        validated = TransactionResponse.model_validate(response.json())
        assert validated.amount == payload["amount"]
        assert validated.type == payload["type"]
        assert validated.currency == "TOMAN"
        assert validated.category_id == payload["category_id"]
        assert validated.note == payload["note"]

    async def test_transaction_get_contract(
        self, async_client: AsyncClient, contract_env: dict
    ) -> None:
        headers = {"Authorization": f"Bearer {contract_env['token']}"}
        response = await async_client.get(
            f"/api/v1/households/{contract_env['household_id']}/transactions/{contract_env['transaction_id']}",
            headers=headers,
        )
        assert response.status_code == 200
        validated = TransactionResponse.model_validate(response.json())
        assert validated.id == contract_env["transaction_id"]
        assert validated.currency == "TOMAN"

    async def test_transaction_get_all_contract(
        self, async_client: AsyncClient, contract_env: dict
    ) -> None:
        headers = {"Authorization": f"Bearer {contract_env['token']}"}
        response = await async_client.get(
            f"/api/v1/households/{contract_env['household_id']}/transactions/",
            headers=headers,
        )
        assert response.status_code == 200
        validated_list = TypeAdapter(list[TransactionResponse]).validate_python(
            response.json()
        )
        assert len(validated_list) >= 1
        assert any(t.id == contract_env["transaction_id"] for t in validated_list)

    async def test_transaction_patch_contract(
        self, async_client: AsyncClient, contract_env: dict
    ) -> None:
        headers = {"Authorization": f"Bearer {contract_env['token']}"}
        payload = {"amount": 420000}
        response = await async_client.patch(
            f"/api/v1/households/{contract_env['household_id']}/transactions/{contract_env['transaction_id']}",
            json=payload,
            headers=headers,
        )
        assert response.status_code == 200
        validated = TransactionResponse.model_validate(response.json())
        assert validated.id == contract_env["transaction_id"]
        assert validated.amount == payload["amount"]

    async def test_compute_summary_contract(
        self, async_client: AsyncClient, contract_env: dict
    ) -> None:
        headers = {"Authorization": f"Bearer {contract_env['token']}"}
        response = await async_client.get(
            f"/api/v1/households/{contract_env['household_id']}/compute/summary",
            headers=headers,
        )
        assert response.status_code == 200
        validated = FinancialSummaryResponse.model_validate(response.json())
        assert validated.currency == "TOMAN"
        assert isinstance(validated.income, int)
        assert isinstance(validated.expense, int)
        assert isinstance(validated.total, int)

    async def test_compute_category_balance_contract(
        self, async_client: AsyncClient, contract_env: dict
    ) -> None:
        headers = {"Authorization": f"Bearer {contract_env['token']}"}
        response = await async_client.get(
            f"/api/v1/households/{contract_env['household_id']}/compute/{contract_env['category_id']}",
            headers=headers,
        )
        assert response.status_code == 200
        validated = CategoryBalanceResponse.model_validate(response.json())
        assert validated.name == "Contract Cat"
        assert validated.budget_goal == 2000000
        assert validated.spent == 150000
        assert validated.remaining == 1850000

    async def test_compute_categories_balance_all_contract(
        self, async_client: AsyncClient, contract_env: dict
    ) -> None:
        headers = {"Authorization": f"Bearer {contract_env['token']}"}
        response = await async_client.get(
            f"/api/v1/households/{contract_env['household_id']}/compute/categories",
            headers=headers,
        )
        assert response.status_code == 200
        validated_list = TypeAdapter(list[CategoryBalanceResponse]).validate_python(
            response.json()
        )
        assert len(validated_list) >= 1
        assert any(c.name == "Contract Cat" for c in validated_list)
