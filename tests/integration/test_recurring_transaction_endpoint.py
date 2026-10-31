from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import (
    Budget,
    Category,
    Household,
    HouseholdMember,
    HouseholdRole,
    User,
)
from app.dependencies import get_uow
from app.domain_models import RecurringTransactionDomain
from app.security import create_access_token, hash_password


@pytest.fixture
async def recurring_endpoint_env(db_session: AsyncSession) -> dict:
    owner = User(
        email="rec_ep_owner@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Recurring EP Owner",
        is_active=True,
    )
    member = User(
        email="rec_ep_member@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Recurring EP Member",
        is_active=True,
    )
    viewer = User(
        email="rec_ep_viewer@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Recurring EP Viewer",
        is_active=True,
    )
    foreign_user = User(
        email="rec_ep_foreign@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Recurring EP Foreign",
        is_active=True,
    )
    db_session.add_all([owner, member, viewer, foreign_user])
    await db_session.flush()

    household_main = Household(name="Recurring Main Household", is_personal=False)
    household_foreign = Household(name="Recurring Foreign Household", is_personal=False)
    db_session.add_all([household_main, household_foreign])
    await db_session.flush()

    memberships = [
        HouseholdMember(
            user_id=owner.id,
            household_id=household_main.id,
            role=HouseholdRole.OWNER,
        ),
        HouseholdMember(
            user_id=member.id,
            household_id=household_main.id,
            role=HouseholdRole.MEMBER,
        ),
        HouseholdMember(
            user_id=viewer.id,
            household_id=household_main.id,
            role=HouseholdRole.VIEWER,
        ),
        HouseholdMember(
            user_id=foreign_user.id,
            household_id=household_foreign.id,
            role=HouseholdRole.OWNER,
        ),
    ]
    db_session.add_all(memberships)

    category = Category(
        name="Gym",
        budget=Budget(goal=2_000_000),
        household_id=household_main.id,
    )
    db_session.add(category)
    await db_session.flush()

    uow = get_uow(db_session)
    template_domain = RecurringTransactionDomain(
        household_id=household_main.id,
        created_by=owner.id,
        amount=100_000,
        type="expense",
        category_id=category.id,
        frequency="daily",
        next_run_date=datetime.now(UTC) + timedelta(days=1),
        is_active=True,
        note="Gym Membership",
    )
    async with uow:
        template = await uow.recurring_transactions.insert_template(template_domain)

    owner_token = create_access_token(subject=str(owner.id))
    member_token = create_access_token(subject=str(member.id))
    viewer_token = create_access_token(subject=str(viewer.id))

    return {
        "owner_token": owner_token,
        "member_token": member_token,
        "viewer_token": viewer_token,
        "household_id": household_main.id,
        "foreign_household_id": household_foreign.id,
        "category_id": category.id,
        "template_id": template.id,
    }


@pytest.mark.asyncio
class TestRecurringTransactionEndpoints:
    async def test_post_transaction_with_frequency(
        self,
        async_client_with_redis: AsyncClient,
        recurring_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {recurring_endpoint_env['owner_token']}"}
        payload = {
            "amount": 250_000,
            "type": "expense",
            "category_id": recurring_endpoint_env["category_id"],
            "frequency": "daily",
            "note": "Daily Commute",
        }

        with patch("app.service.enqueue_recurring_transaction"):
            response = await async_client_with_redis.post(
                f"/api/v1/households/{recurring_endpoint_env['household_id']}/transactions/",
                json=payload,
                headers=headers,
            )

        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 250_000
        assert data["type"] == "expense"
        assert data["category_id"] == recurring_endpoint_env["category_id"]

    async def test_get_recurring_templates(
        self,
        async_client_with_redis: AsyncClient,
        recurring_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {recurring_endpoint_env['member_token']}"}

        response = await async_client_with_redis.get(
            f"/api/v1/households/{recurring_endpoint_env['household_id']}/recurring_transaction/",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        template_ids = [t["id"] for t in data]
        assert recurring_endpoint_env["template_id"] in template_ids

    async def test_get_recurring_templates_as_viewer(
        self,
        async_client_with_redis: AsyncClient,
        recurring_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {recurring_endpoint_env['viewer_token']}"}

        response = await async_client_with_redis.get(
            f"/api/v1/households/{recurring_endpoint_env['household_id']}/recurring_transaction/",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        template_ids = [t["id"] for t in data]
        assert recurring_endpoint_env["template_id"] in template_ids

    async def test_patch_recurring_template_success(
        self,
        async_client_with_redis: AsyncClient,
        recurring_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {recurring_endpoint_env['owner_token']}"}
        template_id = recurring_endpoint_env["template_id"]
        payload = {
            "amount": 120_000,
            "is_active": False,
            "note": "Paused Gym Membership",
        }

        response = await async_client_with_redis.patch(
            f"/api/v1/households/{recurring_endpoint_env['household_id']}/recurring_transaction/{template_id}",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == template_id
        assert data["amount"] == 120_000
        assert data["is_active"] is False
        assert data["note"] == "Paused Gym Membership"

    async def test_patch_recurring_template_forbidden(
        self,
        async_client_with_redis: AsyncClient,
        recurring_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {recurring_endpoint_env['member_token']}"}
        template_id = recurring_endpoint_env["template_id"]
        payload = {"amount": 150_000}

        response = await async_client_with_redis.patch(
            f"/api/v1/households/{recurring_endpoint_env['household_id']}/recurring_transaction/{template_id}",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INSUFFICIENT_PERMISSIONS"

    async def test_patch_recurring_template_viewer_forbidden(
        self,
        async_client_with_redis: AsyncClient,
        recurring_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {recurring_endpoint_env['viewer_token']}"}
        template_id = recurring_endpoint_env["template_id"]
        payload = {"amount": 150_000}

        response = await async_client_with_redis.patch(
            f"/api/v1/households/{recurring_endpoint_env['household_id']}/recurring_transaction/{template_id}",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INSUFFICIENT_PERMISSIONS"

    async def test_delete_recurring_template_success(
        self,
        async_client_with_redis: AsyncClient,
        recurring_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {recurring_endpoint_env['owner_token']}"}
        template_id = recurring_endpoint_env["template_id"]

        response = await async_client_with_redis.delete(
            f"/api/v1/households/{recurring_endpoint_env['household_id']}/recurring_transaction/{template_id}",
            headers=headers,
        )

        assert response.status_code == 204

        get_res = await async_client_with_redis.get(
            f"/api/v1/households/{recurring_endpoint_env['household_id']}/recurring_transaction/",
            headers=headers,
        )
        assert get_res.status_code == 200
        current_ids = [t["id"] for t in get_res.json()]
        assert template_id not in current_ids

    async def test_delete_recurring_template_viewer_forbidden(
        self,
        async_client_with_redis: AsyncClient,
        recurring_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {recurring_endpoint_env['viewer_token']}"}
        template_id = recurring_endpoint_env["template_id"]

        response = await async_client_with_redis.delete(
            f"/api/v1/households/{recurring_endpoint_env['household_id']}/recurring_transaction/{template_id}",
            headers=headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INSUFFICIENT_PERMISSIONS"
