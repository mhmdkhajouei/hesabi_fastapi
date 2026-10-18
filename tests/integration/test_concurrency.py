import asyncio
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db.database import (
    Budget,
    Category,
    Household,
    HouseholdMember,
    HouseholdRole,
    User,
)
from app.dependencies import get_session
from app.main import app
from app.security import create_access_token, hash_password


@pytest.mark.asyncio
async def test_concurrent_transactions_do_not_exceed_budget(test_engine):
    test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

    async def _override_get_session():
        async with test_session_factory() as session:
            try:
                yield session
                await session.commit()
            except BaseException:
                await session.rollback()
                raise

    app.dependency_overrides[get_session] = _override_get_session

    try:
        async with test_session_factory() as session:
            user = User(
                email="test@concurrency.com",
                password_hash=hash_password("pass"),
                name="Test",
            )
            session.add(user)
            await session.flush()

            household = Household(name="Test HH", is_personal=False)
            session.add(household)
            await session.flush()

            session.add(
                HouseholdMember(
                    user_id=user.id, household_id=household.id, role=HouseholdRole.OWNER
                )
            )

            category = Category(
                name="Food", household_id=household.id, budget=Budget(goal=100000)
            )
            session.add(category)
            await session.commit()

            token = create_access_token(subject=str(user.id))
            household_id = household.id
            category_id = category.id

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            headers = {"Authorization": f"Bearer {token}"}
            payload = {
                "amount": 10_000,
                "type": "expense",
                "category_id": category_id,
            }

            tasks = [
                client.post(
                    f"/api/v1/households/{household_id}/transactions/",
                    json=payload,
                    headers=headers,
                )
                for _ in range(20)
            ]
            responses = await asyncio.gather(*tasks)

        success = [r for r in responses if r.status_code == 201]
        failed = [r for r in responses if r.status_code == 422]

        assert len(success) == 10, f"Expected 10 successes, got {len(success)}"
        assert len(failed) == 10, f"Expected 10 failures, got {len(failed)}"

        for r in failed:
            assert r.json()["error_code"] == "BUDGET_LIMIT_EXCEEDED"

        async with test_session_factory() as session:
            result = await session.execute(
                text(
                    "SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM transactions WHERE category_id = :cid"
                ),
                {"cid": category_id},
            )
            count, total = result.one()
            assert count == 10, f"Expected 10 transactions in DB, got {count}"
            assert total == 100_000, f"Expected total 100,000, got {total}"

    finally:
        async with test_engine.begin() as conn:
            await conn.execute(
                text(
                    "TRUNCATE TABLE transactions, budgets, categories, household_members, household, users RESTART IDENTITY CASCADE"
                )
            )

        app.dependency_overrides.clear()
