# tests/integration/test_recurring_worker.py

import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import fakeredis.aioredis
import pytest
import redis.exceptions
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.cache import categories_key, category_key, summary_key
from app.db.database import (
    Budget,
    Category,
    Household,
    HouseholdMember,
    HouseholdRole,
    User,
)
from app.dependencies import (
    get_recurring_transaction_service,
    get_transaction_service,
    get_uow,
)
from app.domain_models import RecurringTransactionDomain
from app.schemas import TransactionCreate
from app.security import hash_password


@pytest.fixture
def recurring_service(
    db_session: AsyncSession,
    fake_redis: fakeredis.aioredis.FakeRedis,
):
    uow = get_uow(db_session)
    return get_recurring_transaction_service(uow, fake_redis)


@pytest.fixture
def transaction_service(
    db_session: AsyncSession,
    fake_redis: fakeredis.aioredis.FakeRedis,
):
    uow = get_uow(db_session)
    return get_transaction_service(uow, fake_redis)


@pytest.fixture
async def worker_env(db_session: AsyncSession) -> dict:
    owner = User(
        email="worker_owner@hesabi.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Worker Owner",
        is_active=True,
    )
    db_session.add(owner)
    await db_session.flush()

    household = Household(name="Worker Household", is_personal=False)
    db_session.add(household)
    await db_session.flush()

    membership = HouseholdMember(
        user_id=owner.id,
        household_id=household.id,
        role=HouseholdRole.OWNER,
    )
    category = Category(
        name="Subscriptions",
        budget=Budget(goal=1_000_000),
        household_id=household.id,
    )
    db_session.add_all([membership, category])
    await db_session.flush()

    past_date = datetime.now(UTC) - timedelta(hours=1)
    template_domain = RecurringTransactionDomain(
        household_id=household.id,
        created_by=owner.id,
        amount=50_000,
        type="expense",
        category_id=category.id,
        frequency="daily",
        next_run_date=past_date,
        is_active=True,
        note="Worker Test Subscription",
    )

    uow = get_uow(db_session)
    async with uow:
        template = await uow.recurring_transactions.insert_template(template_domain)

    return {
        "owner_id": owner.id,
        "household_id": household.id,
        "category_id": category.id,
        "template_id": template.id,
        "scheduled_date": past_date,
    }


class TestRecurringWorker:
    async def test_process_single_template_happy_path(
        self,
        recurring_service,
        worker_env: dict,
        db_session: AsyncSession,
    ):
        template_id = worker_env["template_id"]
        household_id = worker_env["household_id"]

        with patch("app.service.enqueue_recurring_transaction") as mock_enqueue:
            await recurring_service.process_single_template(template_id)

            assert mock_enqueue.called
            call_args = mock_enqueue.call_args[0]
            assert call_args[0] == template_id
            assert call_args[1] >= 0

        uow = get_uow(db_session)
        async with uow:
            txs = await uow.transactions.get_all_transactions(household_id)
            matching = [t for t in txs if t.note == "Worker Test Subscription"]
            assert len(matching) == 1
            assert matching[0].amount == 50_000
            assert matching[0].category_id == worker_env["category_id"]

            updated_template = await uow.recurring_transactions.get_by_id(template_id)
            assert updated_template.next_run_date > worker_env["scheduled_date"]

    async def test_process_single_template_inactive_noop(
        self,
        recurring_service,
        worker_env: dict,
        db_session: AsyncSession,
    ):
        template_id = worker_env["template_id"]
        household_id = worker_env["household_id"]

        uow = get_uow(db_session)
        async with uow:
            tmpl = await uow.recurring_transactions.get_by_id(template_id)
            tmpl.is_active = False
            await uow.session.flush()

        with patch("app.service.enqueue_recurring_transaction") as mock_enqueue:
            await recurring_service.process_single_template(template_id)
            assert not mock_enqueue.called

        async with uow:
            txs = await uow.transactions.get_all_transactions(household_id)
            matching = [t for t in txs if t.note == "Worker Test Subscription"]
            assert len(matching) == 0

    async def test_process_single_template_future_date_noop(
        self,
        recurring_service,
        worker_env: dict,
        db_session: AsyncSession,
    ):
        template_id = worker_env["template_id"]
        household_id = worker_env["household_id"]
        future_date = datetime.now(UTC) + timedelta(days=5)

        uow = get_uow(db_session)
        async with uow:
            tmpl = await uow.recurring_transactions.get_by_id(template_id)
            tmpl.next_run_date = future_date
            await uow.session.flush()

        with patch("app.service.enqueue_recurring_transaction") as mock_enqueue:
            await recurring_service.process_single_template(template_id)
            assert not mock_enqueue.called

        async with uow:
            txs = await uow.transactions.get_all_transactions(household_id)
            matching = [t for t in txs if t.note == "Worker Test Subscription"]
            assert len(matching) == 0

    async def test_process_single_template_category_deleted(
        self,
        recurring_service,
        worker_env: dict,
        db_session: AsyncSession,
    ):
        template_id = worker_env["template_id"]
        household_id = worker_env["household_id"]

        uow = get_uow(db_session)
        async with uow:
            tmpl = await uow.recurring_transactions.get_by_id(template_id)
            tmpl.category_id = None
            await uow.session.flush()

        with patch("app.service.enqueue_recurring_transaction"):
            await recurring_service.process_single_template(template_id)

        async with uow:
            txs = await uow.transactions.get_all_transactions(household_id)
            matching = [t for t in txs if t.note == "Worker Test Subscription"]
            assert len(matching) == 1
            assert matching[0].category_id is None

    async def test_process_single_template_delayed_execution(
        self,
        recurring_service,
        worker_env: dict,
        db_session: AsyncSession,
    ):
        template_id = worker_env["template_id"]
        household_id = worker_env["household_id"]
        scheduled = worker_env["scheduled_date"]

        with patch("app.service.enqueue_recurring_transaction"):
            await recurring_service.process_single_template(template_id)

        uow = get_uow(db_session)
        async with uow:
            txs = await uow.transactions.get_all_transactions(household_id)
            matching = [t for t in txs if t.note == "Worker Test Subscription"]
            assert len(matching) == 1
            assert matching[0].date == scheduled

    async def test_process_single_template_race_condition(
        self,
        test_engine: AsyncEngine,
        fake_redis: fakeredis.aioredis.FakeRedis,
    ):
        session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
        async with session_factory() as session:
            user = User(
                email="race_worker@hesabi.com",
                password_hash=hash_password("StrongPassword123!"),
                name="Race Worker",
                is_active=True,
            )
            household = Household(name="Race Household", is_personal=False)
            session.add_all([user, household])
            await session.flush()

            session.add(
                HouseholdMember(
                    user_id=user.id,
                    household_id=household.id,
                    role=HouseholdRole.OWNER,
                )
            )
            await session.flush()

            template_domain = RecurringTransactionDomain(
                household_id=household.id,
                created_by=user.id,
                amount=75_000,
                type="expense",
                frequency="daily",
                next_run_date=datetime.now(UTC) - timedelta(minutes=10),
                is_active=True,
                note="Race Condition Template",
            )
            uow = get_uow(session)
            async with uow:
                tmpl = await uow.recurring_transactions.insert_template(template_domain)

            household_id = household.id
            template_id = tmpl.id

        async def _run_worker():
            async with session_factory() as session:
                uow = get_uow(session)
                service = get_recurring_transaction_service(uow, fake_redis)
                with patch("app.service.enqueue_recurring_transaction"):
                    await service.process_single_template(template_id)

        await asyncio.gather(_run_worker(), _run_worker(), return_exceptions=True)

        async with session_factory() as session:
            uow = get_uow(session)
            async with uow:
                txs = await uow.transactions.get_all_transactions(household_id)
                matching = [t for t in txs if t.note == "Race Condition Template"]
                assert len(matching) >= 1

    async def test_process_single_template_re_enqueues_next_cycle(
        self,
        recurring_service,
        worker_env: dict,
        db_session: AsyncSession,
    ):
        template_id = worker_env["template_id"]
        expected_next = worker_env["scheduled_date"] + timedelta(days=1)

        with patch("app.service.enqueue_recurring_transaction") as mock_enqueue:
            await recurring_service.process_single_template(template_id)
            assert mock_enqueue.called
            call_args = mock_enqueue.call_args[0]
            assert call_args[0] == template_id

        uow = get_uow(db_session)
        async with uow:
            tmpl = await uow.recurring_transactions.get_by_id(template_id)
            assert tmpl.next_run_date == expected_next

    async def test_process_single_template_cache_invalidation_call(
        self,
        recurring_service,
        worker_env: dict,
        fake_redis: fakeredis.aioredis.FakeRedis,
    ):
        template_id = worker_env["template_id"]
        household_id = worker_env["household_id"]
        category_id = worker_env["category_id"]

        with (
            patch("app.service.enqueue_recurring_transaction"),
            patch(
                "app.service.invalidate_compute_cache", new_callable=AsyncMock
            ) as mock_invalidate,
        ):
            await recurring_service.process_single_template(template_id)
            mock_invalidate.assert_awaited_once_with(
                fake_redis, household_id, [category_id]
            )

    async def test_process_single_template_deleted_between_enqueue_and_run(
        self,
        recurring_service,
    ):
        with patch("app.service.enqueue_recurring_transaction") as mock_enqueue:
            result = await recurring_service.process_single_template(999_999)
            assert result is None
            assert not mock_enqueue.called

    async def test_process_single_template_delay_seconds_non_negative(
        self,
        recurring_service,
        worker_env: dict,
        db_session: AsyncSession,
    ):
        template_id = worker_env["template_id"]
        past_date = datetime.now(UTC) - timedelta(days=10)

        uow = get_uow(db_session)
        async with uow:
            tmpl = await uow.recurring_transactions.get_by_id(template_id)
            tmpl.next_run_date = past_date
            await uow.session.flush()

        with patch("app.service.enqueue_recurring_transaction") as mock_enqueue:
            await recurring_service.process_single_template(template_id)
            assert mock_enqueue.called
            delay = mock_enqueue.call_args[0][1]
            assert delay >= 0.0

    async def test_process_single_template_redis_failure(
        self,
        recurring_service,
        worker_env: dict,
        fake_redis: fakeredis.aioredis.FakeRedis,
        db_session: AsyncSession,
    ):
        template_id = worker_env["template_id"]
        household_id = worker_env["household_id"]

        with (
            patch("app.service.enqueue_recurring_transaction"),
            patch.object(
                fake_redis,
                "delete",
                side_effect=redis.exceptions.ConnectionError("Redis connection down"),
            ),pytest.raises(redis.exceptions.ConnectionError)
        ):
            await recurring_service.process_single_template(template_id)

        uow = get_uow(db_session)
        async with uow:
            txs = await uow.transactions.get_all_transactions(household_id)
            matching = [t for t in txs if t.note == "Worker Test Subscription"]
            assert len(matching) == 1

    async def test_cache_invalidation_after_worker_runs(
        self,
        recurring_service,
        worker_env: dict,
        fake_redis: fakeredis.aioredis.FakeRedis,
    ):
        template_id = worker_env["template_id"]
        household_id = worker_env["household_id"]
        category_id = worker_env["category_id"]

        s_key = summary_key(household_id)
        c_key = category_key(household_id, category_id)
        all_c_key = categories_key(household_id)

        await fake_redis.set(s_key, "summary_data")
        await fake_redis.set(c_key, "cat_data")
        await fake_redis.set(all_c_key, "all_cat_data")

        with patch("app.service.enqueue_recurring_transaction"):
            await recurring_service.process_single_template(template_id)

        assert await fake_redis.get(s_key) is None
        assert await fake_redis.get(c_key) is None
        assert await fake_redis.get(all_c_key) is None

    async def test_transaction_and_template_atomicity(
        self,
        transaction_service,
        worker_env: dict,
        db_session: AsyncSession,
    ):
        household_id = worker_env["household_id"]
        owner_id = worker_env["owner_id"]
        category_id = worker_env["category_id"]

        payload = TransactionCreate(
            amount=80_000,
            type="expense",
            category_id=category_id,
            frequency="daily",
            note="Atomic Transaction",
        )

        with patch(
            "app.db.crud.RecurringTransactionRepo.insert_template",
            side_effect=RuntimeError("Template insertion failed"),
        ), pytest.raises(RuntimeError):
            await transaction_service.add_transaction(
                household_id=household_id,
                user_id=owner_id,
                data=payload,
                user_role=HouseholdRole.OWNER,
            )

        uow = get_uow(db_session)
        async with uow:
            txs = await uow.transactions.get_all_transactions(household_id)
            matching = [t for t in txs if t.note == "Atomic Transaction"]
            assert len(matching) == 0

            templates = await uow.recurring_transactions.get_all_templates(household_id)
            matching_templates = [
                t for t in templates if t.note == "Atomic Transaction"
            ]
            assert len(matching_templates) == 0

    async def test_budget_limit_with_recurring_transactions(
        self,
        recurring_service,
        worker_env: dict,
        db_session: AsyncSession,
    ):
        template_id = worker_env["template_id"]
        household_id = worker_env["household_id"]
        category_id = worker_env["category_id"]

        uow = get_uow(db_session)
        async with uow:
            spent_before = await uow.compute.get_category_total_spent(
                household_id=household_id,
                category_id=category_id,
            )

        with patch("app.service.enqueue_recurring_transaction"):
            await recurring_service.process_single_template(template_id)

        async with uow:
            spent_after = await uow.compute.get_category_total_spent(
                household_id=household_id,
                category_id=category_id,
            )
            assert spent_after == spent_before + 50_000

    async def test_worker_graceful_shutdown(
        self,
        recurring_service,
        worker_env: dict,
        db_session: AsyncSession,
    ):
        template_id = worker_env["template_id"]
        household_id = worker_env["household_id"]

        with patch(
            "app.service.enqueue_recurring_transaction",
            side_effect=asyncio.CancelledError("Worker interrupted"),
        ), pytest.raises(asyncio.CancelledError):
            await recurring_service.process_single_template(template_id)

        uow = get_uow(db_session)
        async with uow:
            txs = await uow.transactions.get_all_transactions(household_id)
            matching = [t for t in txs if t.note == "Worker Test Subscription"]
            assert len(matching) == 1
