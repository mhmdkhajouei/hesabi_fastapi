from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import select
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
async def transaction_test_env(db_session: AsyncSession) -> dict:
    owner = User(
        email="tx_owner@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Tx Owner",
        is_active=True,
    )
    member_alice = User(
        email="tx_alice@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Tx Alice",
        is_active=True,
    )
    member_bob = User(
        email="tx_bob@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Tx Bob",
        is_active=True,
    )
    viewer = User(
        email="tx_viewer@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Tx Viewer",
        is_active=True,
    )
    db_session.add_all([owner, member_alice, member_bob, viewer])
    await db_session.commit()
    await db_session.refresh(owner)
    await db_session.refresh(member_alice)
    await db_session.refresh(member_bob)
    await db_session.refresh(viewer)

    household_main = Household(name="Main Household")
    household_foreign = Household(name="Foreign Household")
    db_session.add_all([household_main, household_foreign])
    await db_session.commit()
    await db_session.refresh(household_main)
    await db_session.refresh(household_foreign)

    db_session.add_all(
        [
            HouseholdMember(
                user_id=owner.id,
                household_id=household_main.id,
                role=HouseholdRole.OWNER,
            ),
            HouseholdMember(
                user_id=member_alice.id,
                household_id=household_main.id,
                role=HouseholdRole.MEMBER,
            ),
            HouseholdMember(
                user_id=member_bob.id,
                household_id=household_main.id,
                role=HouseholdRole.MEMBER,
            ),
            HouseholdMember(
                user_id=viewer.id,
                household_id=household_main.id,
                role=HouseholdRole.VIEWER,
            ),
        ]
    )

    category_main = Category(
        name="Utilities",
        budget=Budget(goal=2000000),
        household_id=household_main.id,
    )
    category_foreign = Category(
        name="Foreign Cat",
        budget=Budget(goal=1000000),
        household_id=household_foreign.id,
    )
    db_session.add_all([category_main, category_foreign])
    await db_session.commit()
    await db_session.refresh(category_main)
    await db_session.refresh(category_foreign)

    return {
        "owner_token": create_access_token(subject=str(owner.id)),
        "alice_token": create_access_token(subject=str(member_alice.id)),
        "bob_token": create_access_token(subject=str(member_bob.id)),
        "viewer_token": create_access_token(subject=str(viewer.id)),
        "alice_id": member_alice.id,
        "bob_id": member_bob.id,
        "household_id": household_main.id,
        "foreign_household_id": household_foreign.id,
        "category_id": category_main.id,
        "foreign_category_id": category_foreign.id,
    }


@pytest.fixture
async def alice_transaction(
    db_session: AsyncSession, transaction_test_env: dict
) -> Transaction:
    tx = Transaction(
        amount=250000,
        type="expense",
        household_id=transaction_test_env["household_id"],
        created_by=transaction_test_env["alice_id"],
        category_id=transaction_test_env["category_id"],
        date=datetime.now(UTC),
        note="Electricity Bill",
    )
    db_session.add(tx)
    await db_session.commit()
    await db_session.refresh(tx)
    return tx


@pytest.mark.asyncio
class TestTransactionEndpoints:
    async def test_create_expense_transaction_happy_path(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        transaction_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['alice_token']}"}
        payload = {
            "amount": 150000,
            "type": "expense",
            "category_id": transaction_test_env["category_id"],
            "note": "Water Bill",
            "date": "2026-09-01T10:00:00Z",
        }

        response = await async_client.post(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["amount"] == payload["amount"]
        assert data["type"] == payload["type"]
        assert data["category_id"] == payload["category_id"]
        assert data["currency"] == "TOMAN"
        assert data["note"] == payload["note"]

        query = select(Transaction).where(Transaction.id == data["id"])
        result = await db_session.execute(query)
        tx_in_db = result.scalar_one_or_none()
        assert tx_in_db is not None
        assert tx_in_db.amount == payload["amount"]
        assert tx_in_db.created_by == transaction_test_env["alice_id"]

    async def test_create_income_transaction_without_category(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        transaction_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['owner_token']}"}
        payload = {
            "amount": 12000000,
            "type": "income",
            "note": "Monthly Salary",
        }

        response = await async_client.post(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "income"
        assert data["category_id"] is None
        assert data["amount"] == payload["amount"]

        query = select(Transaction).where(Transaction.id == data["id"])
        result = await db_session.execute(query)
        tx_in_db = result.scalar_one()
        assert tx_in_db.category_id is None

    async def test_create_transaction_amount_boundary(
        self,
        async_client: AsyncClient,
        transaction_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['alice_token']}"}
        payload = {
            "amount": 1,
            "type": "expense",
            "category_id": transaction_test_env["category_id"],
        }

        response = await async_client.post(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 201
        assert response.json()["amount"] == 1

    async def test_create_transaction_note_boundary(
        self,
        async_client: AsyncClient,
        transaction_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['alice_token']}"}
        payload_valid = {
            "amount": 50000,
            "type": "expense",
            "note": "N" * 225,
        }

        response_valid = await async_client.post(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/",
            json=payload_valid,
            headers=headers,
        )
        assert response_valid.status_code == 201

        payload_invalid = {
            "amount": 50000,
            "type": "expense",
            "note": "N" * 226,
        }
        response_invalid = await async_client.post(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/",
            json=payload_invalid,
            headers=headers,
        )
        assert response_invalid.status_code == 422
        assert response_invalid.json()["error_code"] == "VALIDATION_ERROR"

    async def test_create_transaction_nonexistent_category(
        self,
        async_client: AsyncClient,
        transaction_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['alice_token']}"}
        payload = {
            "amount": 50000,
            "type": "expense",
            "category_id": 999999,
        }

        response = await async_client.post(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "CATEGORY_NOT_FOUND"
        assert data["message"] == "Category with ID 999999 not found"

    async def test_create_transaction_foreign_category_cross_household_bola(
        self,
        async_client: AsyncClient,
        transaction_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['alice_token']}"}
        payload = {
            "amount": 50000,
            "type": "expense",
            "category_id": transaction_test_env["foreign_category_id"],
        }

        response = await async_client.post(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "CATEGORY_NOT_FOUND"

    async def test_create_transaction_viewer_forbidden(
        self,
        async_client: AsyncClient,
        transaction_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['viewer_token']}"}
        payload = {
            "amount": 50000,
            "type": "income",
        }

        response = await async_client.post(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INSUFFICIENT_PERMISSIONS"

    @pytest.mark.parametrize(
        "invalid_payload",
        [
            {"amount": 0, "type": "expense"},
            {"amount": -500, "type": "expense"},
            {"amount": 50000, "type": "transfer"},
            {"amount": 50000, "type": "expense", "category_id": 0},
            {"amount": 50000, "type": "expense", "category_id": -10},
            {"type": "income"},
        ],
    )
    async def test_create_transaction_validation_errors(
        self,
        async_client: AsyncClient,
        transaction_test_env: dict,
        invalid_payload: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['alice_token']}"}

        response = await async_client.post(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/",
            json=invalid_payload,
            headers=headers,
        )

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "VALIDATION_ERROR"
        assert len(data["errors"]) > 0

    async def test_get_transaction_by_id_happy_path(
        self,
        async_client: AsyncClient,
        transaction_test_env: dict,
        alice_transaction: Transaction,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['viewer_token']}"}

        response = await async_client.get(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/{alice_transaction.id}",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == alice_transaction.id
        assert data["amount"] == alice_transaction.amount
        assert data["type"] == alice_transaction.type

    async def test_get_transaction_not_found(
        self,
        async_client: AsyncClient,
        transaction_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['owner_token']}"}

        response = await async_client.get(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/999999",
            headers=headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "TRANSACTION_NOT_FOUND"
        assert data["message"] == "Transaction with id 999999 not found"

    async def test_get_transaction_cross_household_bola_protection(
        self,
        async_client: AsyncClient,
        transaction_test_env: dict,
        alice_transaction: Transaction,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['owner_token']}"}

        response = await async_client.get(
            f"/api/v1/households/{transaction_test_env['foreign_household_id']}/transactions/{alice_transaction.id}",
            headers=headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "HOUSEHOLD_NOT_FOUND"

    async def test_get_all_transactions_happy_path(
        self,
        async_client: AsyncClient,
        transaction_test_env: dict,
        alice_transaction: Transaction,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['bob_token']}"}

        response = await async_client.get(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(item["id"] == alice_transaction.id for item in data)

    async def test_patch_transaction_by_creator_member(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        transaction_test_env: dict,
        alice_transaction: Transaction,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['alice_token']}"}
        payload = {"amount": 280000, "note": "Updated Electricity Bill"}

        response = await async_client.patch(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/{alice_transaction.id}",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 280000
        assert data["note"] == "Updated Electricity Bill"

        query = select(Transaction).where(Transaction.id == alice_transaction.id)
        result = await db_session.execute(query)
        tx_in_db = result.scalar_one()
        assert tx_in_db.amount == 280000
        assert tx_in_db.note == "Updated Electricity Bill"

    async def test_patch_transaction_by_owner_on_member_transaction(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        transaction_test_env: dict,
        alice_transaction: Transaction,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['owner_token']}"}
        payload = {"amount": 300000}

        response = await async_client.patch(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/{alice_transaction.id}",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json()["amount"] == 300000

        query = select(Transaction).where(Transaction.id == alice_transaction.id)
        result = await db_session.execute(query)
        assert result.scalar_one().amount == 300000

    async def test_patch_transaction_other_member_forbidden(
        self,
        async_client: AsyncClient,
        transaction_test_env: dict,
        alice_transaction: Transaction,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['bob_token']}"}
        payload = {"amount": 999999}

        response = await async_client.patch(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/{alice_transaction.id}",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INSUFFICIENT_PERMISSIONS"
        assert data["message"] == "You can only edit your own transaction"

    async def test_patch_transaction_type_income_resets_category(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        transaction_test_env: dict,
        alice_transaction: Transaction,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['alice_token']}"}
        payload = {"type": "income"}

        response = await async_client.patch(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/{alice_transaction.id}",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "income"
        assert data["category_id"] is None

        query = select(Transaction).where(Transaction.id == alice_transaction.id)
        result = await db_session.execute(query)
        assert result.scalar_one().category_id is None

    async def test_delete_transaction_other_member_forbidden(
        self,
        async_client: AsyncClient,
        transaction_test_env: dict,
        alice_transaction: Transaction,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['bob_token']}"}

        response = await async_client.delete(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/{alice_transaction.id}",
            headers=headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INSUFFICIENT_PERMISSIONS"
        assert data["message"] == "You can only delete your own transaction"

    async def test_delete_transaction_by_creator_member(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        transaction_test_env: dict,
        alice_transaction: Transaction,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['alice_token']}"}

        response = await async_client.delete(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/{alice_transaction.id}",
            headers=headers,
        )

        assert response.status_code == 204
        assert response.content == b""

        query = select(Transaction).where(Transaction.id == alice_transaction.id)
        result = await db_session.execute(query)
        assert result.scalar_one_or_none() is None

    async def test_delete_transaction_by_owner(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        transaction_test_env: dict,
        alice_transaction: Transaction,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['owner_token']}"}

        response = await async_client.delete(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/{alice_transaction.id}",
            headers=headers,
        )

        assert response.status_code == 204
        assert response.content == b""

        query = select(Transaction).where(Transaction.id == alice_transaction.id)
        result = await db_session.execute(query)
        assert result.scalar_one_or_none() is None

    async def test_delete_transaction_not_found(
        self,
        async_client: AsyncClient,
        transaction_test_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {transaction_test_env['owner_token']}"}

        response = await async_client.delete(
            f"/api/v1/households/{transaction_test_env['household_id']}/transactions/999999",
            headers=headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "TRANSACTION_NOT_FOUND"
        assert data["message"] == "Transaction with id 999999 not found"
