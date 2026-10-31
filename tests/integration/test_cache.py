import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import categories_key, category_key, summary_key
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
async def cache_env(db_session: AsyncSession) -> dict:
    owner = User(
        email="cache_owner@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Cache Owner",
        is_active=True,
    )
    db_session.add(owner)
    await db_session.flush()

    household = Household(name="Cache Household")
    db_session.add(household)
    await db_session.flush()

    db_session.add(
        HouseholdMember(
            user_id=owner.id,
            household_id=household.id,
            role=HouseholdRole.OWNER,
        )
    )
    await db_session.flush()

    category_a = Category(
        name="Cat A", budget=Budget(goal=1_000_000), household_id=household.id
    )
    category_b = Category(
        name="Cat B", budget=Budget(goal=500_000), household_id=household.id
    )
    db_session.add_all([category_a, category_b])
    await db_session.flush()

    return {
        "owner_id": owner.id,
        "owner_token": create_access_token(subject=str(owner.id)),
        "household_id": household.id,
        "category_a_id": category_a.id,
        "category_b_id": category_b.id,
    }


@pytest.mark.asyncio
class TestCacheAside:
    async def test_summary_cache_lifecycle(
        self, async_client_with_redis: AsyncClient, cache_env: dict, fake_redis
    ):
        headers = {"Authorization": f"Bearer {cache_env['owner_token']}"}
        h_id = cache_env["household_id"]
        c_id = cache_env["category_a_id"]
        key = summary_key(h_id)

        assert await fake_redis.get(key) is None

        r1 = await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/summary", headers=headers
        )
        assert r1.status_code == 200
        data_1 = r1.json()
        assert data_1["income"] == 0
        assert data_1["expense"] == 0
        assert data_1["total"] == 0
        assert await fake_redis.get(key) is not None

        r2 = await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/summary", headers=headers
        )
        assert r2.status_code == 200
        assert r2.json() == data_1

        r_tx = await async_client_with_redis.post(
            f"/api/v1/households/{h_id}/transactions/",
            json={"amount": 5000, "type": "expense", "category_id": c_id},
            headers=headers,
        )
        assert r_tx.status_code == 201
        assert await fake_redis.get(key) is None

        r3 = await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/summary", headers=headers
        )
        assert r3.status_code == 200
        data_3 = r3.json()
        assert data_3["expense"] == 5000
        assert data_3["total"] == -5000
        assert await fake_redis.get(key) is not None

        r4 = await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/summary", headers=headers
        )
        assert r4.status_code == 200
        assert r4.json() == data_3

    async def test_category_balance_cache_lifecycle(
        self, async_client_with_redis: AsyncClient, cache_env: dict, fake_redis
    ):
        headers = {"Authorization": f"Bearer {cache_env['owner_token']}"}
        h_id = cache_env["household_id"]
        c_id = cache_env["category_a_id"]
        key = category_key(h_id, c_id)

        assert await fake_redis.get(key) is None

        r1 = await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/{c_id}", headers=headers
        )
        assert r1.status_code == 200
        data_1 = r1.json()
        assert data_1["budget_goal"] == 1_000_000
        assert data_1["spent"] == 0
        assert data_1["remaining"] == 1_000_000
        assert await fake_redis.get(key) is not None

        r2 = await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/{c_id}", headers=headers
        )
        assert r2.status_code == 200
        assert r2.json() == data_1

        r_patch = await async_client_with_redis.patch(
            f"/api/v1/households/{h_id}/categories/{c_id}",
            json={"budget_goal": 2_000_000},
            headers=headers,
        )
        assert r_patch.status_code == 200
        assert await fake_redis.get(key) is None

        r3 = await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/{c_id}", headers=headers
        )
        assert r3.status_code == 200
        data_3 = r3.json()
        assert data_3["budget_goal"] == 2_000_000
        assert data_3["spent"] == 0
        assert data_3["remaining"] == 2_000_000
        assert await fake_redis.get(key) is not None

        r4 = await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/{c_id}", headers=headers
        )
        assert r4.status_code == 200
        assert r4.json() == data_3

    async def test_categories_balance_cache_lifecycle(
        self,
        async_client_with_redis: AsyncClient,
        cache_env: dict,
        fake_redis,
        db_session,
    ):
        headers = {"Authorization": f"Bearer {cache_env['owner_token']}"}
        h_id = cache_env["household_id"]
        c_a_id = cache_env["category_a_id"]
        c_b_id = cache_env["category_b_id"]
        key = categories_key(h_id)

        assert await fake_redis.get(key) is None

        r1 = await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/categories", headers=headers
        )
        assert r1.status_code == 200
        data_1 = r1.json()
        assert len(data_1) == 2
        cat_a_res = next(c for c in data_1 if c["name"] == "Cat A")
        cat_b_res = next(c for c in data_1 if c["name"] == "Cat B")
        assert cat_a_res["budget_goal"] == 1_000_000
        assert cat_b_res["budget_goal"] == 500_000
        assert await fake_redis.get(key) is not None

        r2 = await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/categories", headers=headers
        )
        assert r2.status_code == 200
        assert r2.json() == data_1

        await async_client_with_redis.post(
            f"/api/v1/households/{h_id}/transactions/",
            json={"amount": 5000, "type": "expense", "category_id": c_a_id},
            headers=headers,
        )
        assert await fake_redis.get(key) is None

        r3 = await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/categories", headers=headers
        )
        assert r3.status_code == 200
        data_3 = r3.json()
        cat_a_res_3 = next(c for c in data_3 if c["name"] == "Cat A")
        cat_b_res_3 = next(c for c in data_3 if c["name"] == "Cat B")
        assert cat_a_res_3["spent"] == 5000
        assert cat_a_res_3["remaining"] == 995_000
        assert cat_b_res_3["spent"] == 0
        assert cat_b_res_3["remaining"] == 500_000
        assert await fake_redis.get(key) is not None

    async def test_empty_household_summary_is_cached(
        self, async_client_with_redis: AsyncClient, cache_env: dict, fake_redis
    ):
        headers = {"Authorization": f"Bearer {cache_env['owner_token']}"}
        h_id = cache_env["household_id"]
        key = summary_key(h_id)

        r = await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/summary", headers=headers
        )
        assert r.status_code == 200
        assert r.json() == {"income": 0, "expense": 0, "total": 0, "currency": "TOMAN"}
        assert await fake_redis.get(key) is not None


@pytest.mark.asyncio
class TestCacheInvalidation:
    async def test_invalidate_on_category_add(
        self, async_client_with_redis: AsyncClient, cache_env: dict, fake_redis
    ):
        headers = {"Authorization": f"Bearer {cache_env['owner_token']}"}
        h_id = cache_env["household_id"]

        await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/summary", headers=headers
        )
        await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/categories", headers=headers
        )
        assert await fake_redis.get(summary_key(h_id)) is not None
        assert await fake_redis.get(categories_key(h_id)) is not None

        r = await async_client_with_redis.post(
            f"/api/v1/households/{h_id}/categories/",
            json={"name": "New Cat", "budget_goal": 100_000},
            headers=headers,
        )
        assert r.status_code == 201
        assert await fake_redis.get(summary_key(h_id)) is None
        assert await fake_redis.get(categories_key(h_id)) is None

    async def test_invalidate_on_category_budget_change_isolated_to_that_category(
        self, async_client_with_redis: AsyncClient, cache_env: dict, fake_redis
    ):
        headers = {"Authorization": f"Bearer {cache_env['owner_token']}"}
        h_id = cache_env["household_id"]
        c_a = cache_env["category_a_id"]
        c_b = cache_env["category_b_id"]

        await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/{c_a}", headers=headers
        )
        await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/{c_b}", headers=headers
        )
        assert await fake_redis.get(category_key(h_id, c_a)) is not None
        assert await fake_redis.get(category_key(h_id, c_b)) is not None

        r = await async_client_with_redis.patch(
            f"/api/v1/households/{h_id}/categories/{c_a}",
            json={"budget_goal": 900_000},
            headers=headers,
        )
        assert r.status_code == 200
        assert await fake_redis.get(category_key(h_id, c_a)) is None
        assert await fake_redis.get(category_key(h_id, c_b)) is not None

    async def test_invalidate_on_transaction_add(
        self, async_client_with_redis: AsyncClient, cache_env: dict, fake_redis
    ):
        headers = {"Authorization": f"Bearer {cache_env['owner_token']}"}
        h_id = cache_env["household_id"]
        cat_a_id = cache_env["category_a_id"]

        await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/summary", headers=headers
        )
        await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/categories", headers=headers
        )
        await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/{cat_a_id}", headers=headers
        )
        assert await fake_redis.get(summary_key(h_id)) is not None
        assert await fake_redis.get(categories_key(h_id)) is not None
        assert await fake_redis.get(category_key(h_id, cat_a_id)) is not None

        r = await async_client_with_redis.post(
            f"/api/v1/households/{h_id}/transactions/",
            json={"amount": 5000, "type": "expense", "category_id": cat_a_id},
            headers=headers,
        )
        assert r.status_code == 201
        assert await fake_redis.get(summary_key(h_id)) is None
        assert await fake_redis.get(categories_key(h_id)) is None
        assert await fake_redis.get(category_key(h_id, cat_a_id)) is None

    async def test_not_invalidated_on_failed_transaction(
        self, async_client_with_redis: AsyncClient, cache_env: dict, fake_redis
    ):
        headers = {"Authorization": f"Bearer {cache_env['owner_token']}"}
        h_id = cache_env["household_id"]
        cat_a_id = cache_env["category_a_id"]

        await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/summary", headers=headers
        )
        assert await fake_redis.get(summary_key(h_id)) is not None

        r = await async_client_with_redis.post(
            f"/api/v1/households/{h_id}/transactions/",
            json={"amount": 2_000_000, "type": "expense", "category_id": cat_a_id},
            headers=headers,
        )
        assert r.status_code == 422
        assert r.json()["error_code"] == "BUDGET_LIMIT_EXCEEDED"
        assert await fake_redis.get(summary_key(h_id)) is not None

    async def test_invalidate_on_category_change_in_transaction(
        self, async_client_with_redis: AsyncClient, cache_env: dict, fake_redis
    ):
        headers = {"Authorization": f"Bearer {cache_env['owner_token']}"}
        h_id = cache_env["household_id"]
        cat_a_id = cache_env["category_a_id"]
        cat_b_id = cache_env["category_b_id"]

        r = await async_client_with_redis.post(
            f"/api/v1/households/{h_id}/transactions/",
            json={"amount": 5000, "type": "expense", "category_id": cat_a_id},
            headers=headers,
        )
        assert r.status_code == 201
        tx_id = r.json()["id"]

        await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/{cat_a_id}", headers=headers
        )
        await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/{cat_b_id}", headers=headers
        )
        assert await fake_redis.get(category_key(h_id, cat_a_id)) is not None
        assert await fake_redis.get(category_key(h_id, cat_b_id)) is not None

        r_patch = await async_client_with_redis.patch(
            f"/api/v1/households/{h_id}/transactions/{tx_id}",
            json={"category_id": cat_b_id},
            headers=headers,
        )
        assert r_patch.status_code == 200
        assert await fake_redis.get(category_key(h_id, cat_a_id)) is None
        assert await fake_redis.get(category_key(h_id, cat_b_id)) is None

    async def test_invalidate_on_type_change_expense_to_income(
        self, async_client_with_redis: AsyncClient, cache_env: dict, fake_redis
    ):
        headers = {"Authorization": f"Bearer {cache_env['owner_token']}"}
        h_id = cache_env["household_id"]
        cat_a_id = cache_env["category_a_id"]

        r = await async_client_with_redis.post(
            f"/api/v1/households/{h_id}/transactions/",
            json={"amount": 5000, "type": "expense", "category_id": cat_a_id},
            headers=headers,
        )
        assert r.status_code == 201
        tx_id = r.json()["id"]

        await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/{cat_a_id}", headers=headers
        )
        assert await fake_redis.get(category_key(h_id, cat_a_id)) is not None

        r_patch = await async_client_with_redis.patch(
            f"/api/v1/households/{h_id}/transactions/{tx_id}",
            json={"type": "income"},
            headers=headers,
        )
        assert r_patch.status_code == 200
        assert await fake_redis.get(category_key(h_id, cat_a_id)) is None
        assert await fake_redis.get(f"compute:category:{h_id}:None") is None

    async def test_invalidate_on_transaction_delete(
        self, async_client_with_redis: AsyncClient, cache_env: dict, fake_redis
    ):
        headers = {"Authorization": f"Bearer {cache_env['owner_token']}"}
        h_id = cache_env["household_id"]
        cat_a_id = cache_env["category_a_id"]

        r = await async_client_with_redis.post(
            f"/api/v1/households/{h_id}/transactions/",
            json={"amount": 5000, "type": "expense", "category_id": cat_a_id},
            headers=headers,
        )
        assert r.status_code == 201
        tx_id = r.json()["id"]

        await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/{cat_a_id}", headers=headers
        )
        await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/summary", headers=headers
        )
        assert await fake_redis.get(category_key(h_id, cat_a_id)) is not None
        assert await fake_redis.get(summary_key(h_id)) is not None

        r_del = await async_client_with_redis.delete(
            f"/api/v1/households/{h_id}/transactions/{tx_id}", headers=headers
        )
        assert r_del.status_code == 204
        assert await fake_redis.get(category_key(h_id, cat_a_id)) is None
        assert await fake_redis.get(summary_key(h_id)) is None

    async def test_not_invalidated_on_404(
        self, async_client_with_redis: AsyncClient, cache_env: dict, fake_redis
    ):
        headers = {"Authorization": f"Bearer {cache_env['owner_token']}"}
        h_id = cache_env["household_id"]

        r = await async_client_with_redis.get(
            f"/api/v1/households/{h_id}/compute/999_999", headers=headers
        )
        assert r.status_code == 404
        assert r.json()["error_code"] == "CATEGORY_NOT_FOUND"
        assert await fake_redis.get(category_key(h_id, 999_999)) is None


@pytest.mark.asyncio
class TestCacheIsolation:
    async def test_cross_household_isolation(
        self,
        async_client_with_redis: AsyncClient,
        cache_env: dict,
        fake_redis,
        db_session,
    ):
        headers = {"Authorization": f"Bearer {cache_env['owner_token']}"}
        h_a = cache_env["household_id"]
        cat_a_id = cache_env["category_a_id"]

        h_b = Household(name="Household B")
        db_session.add(h_b)
        await db_session.flush()
        cat_b = Category(name="Cat B", budget=Budget(goal=500_000), household_id=h_b.id)
        db_session.add(cat_b)
        await db_session.flush()
        db_session.add(
            HouseholdMember(
                user_id=cache_env["owner_id"],
                household_id=h_b.id,
                role=HouseholdRole.OWNER,
            )
        )
        await db_session.flush()

        r_a = await async_client_with_redis.get(
            f"/api/v1/households/{h_a}/compute/summary", headers=headers
        )
        r_b = await async_client_with_redis.get(
            f"/api/v1/households/{h_b.id}/compute/summary", headers=headers
        )
        assert r_a.json()["total"] == 0
        assert r_b.json()["total"] == 0
        assert await fake_redis.get(summary_key(h_a)) is not None
        assert await fake_redis.get(summary_key(h_b.id)) is not None

        r_write = await async_client_with_redis.post(
            f"/api/v1/households/{h_a}/transactions/",
            json={"amount": 5000, "type": "expense", "category_id": cat_a_id},
            headers=headers,
        )
        assert r_write.status_code == 201

        assert await fake_redis.get(summary_key(h_a)) is None
        assert await fake_redis.get(summary_key(h_b.id)) is not None

        r_a2 = await async_client_with_redis.get(
            f"/api/v1/households/{h_a}/compute/summary", headers=headers
        )
        assert r_a2.json()["expense"] == 5000
        r_b2 = await async_client_with_redis.get(
            f"/api/v1/households/{h_b.id}/compute/summary", headers=headers
        )
        assert r_b2.json() == r_b.json()
