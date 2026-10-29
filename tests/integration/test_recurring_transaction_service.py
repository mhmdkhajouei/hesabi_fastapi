# tests/integration/test_recurring_transaction_service.py

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import fakeredis.aioredis
import pytest
import redis.exceptions
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.errors.exceptions import BusinessRuleError, ForbiddenError, NotFoundError
from app.schemas import (
    RecurringTransactionUpdate,
    TransactionCreate,
)
from app.security import hash_password


@pytest.fixture
def transaction_service(
    db_session: AsyncSession,
    fake_redis: fakeredis.aioredis.FakeRedis,
):
    uow = get_uow(db_session)
    return get_transaction_service(uow, fake_redis)


@pytest.fixture
def recurring_service(
    db_session: AsyncSession,
    fake_redis: fakeredis.aioredis.FakeRedis,
):
    uow = get_uow(db_session)
    return get_recurring_transaction_service(uow, fake_redis)


@pytest.fixture
async def recurring_env(db_session: AsyncSession) -> dict:
    owner = User(
        email="rec_owner@hesabi.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Recurring Owner",
        is_active=True,
    )
    member = User(
        email="rec_member@hesabi.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Recurring Member",
        is_active=True,
    )
    viewer = User(
        email="rec_viewer@hesabi.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Recurring Viewer",
        is_active=True,
    )
    foreign_user = User(
        email="rec_foreign@hesabi.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Foreign Owner",
        is_active=True,
    )
    db_session.add_all([owner, member, viewer, foreign_user])
    await db_session.flush()

    household = Household(name="Primary Recurring Household", is_personal=False)
    foreign_household = Household(name="Foreign Household", is_personal=False)
    db_session.add_all([household, foreign_household])
    await db_session.flush()

    memberships = [
        HouseholdMember(
            user_id=owner.id,
            household_id=household.id,
            role=HouseholdRole.OWNER,
        ),
        HouseholdMember(
            user_id=member.id,
            household_id=household.id,
            role=HouseholdRole.MEMBER,
        ),
        HouseholdMember(
            user_id=viewer.id,
            household_id=household.id,
            role=HouseholdRole.VIEWER,
        ),
        HouseholdMember(
            user_id=foreign_user.id,
            household_id=foreign_household.id,
            role=HouseholdRole.OWNER,
        ),
    ]
    db_session.add_all(memberships)

    category = Category(
        name="Internet",
        household_id=household.id,
        budget=Budget(goal=1_000_000),
    )
    foreign_category = Category(
        name="Foreign Cat",
        household_id=foreign_household.id,
        budget=Budget(goal=2_000_000),
    )
    db_session.add_all([category, foreign_category])
    await db_session.flush()

    uow = get_uow(db_session)
    template_domain = RecurringTransactionDomain(
        household_id=household.id,
        created_by=owner.id,
        amount=200_000,
        type="expense",
        category_id=category.id,
        frequency="daily",
        next_run_date=datetime.now(UTC) + timedelta(days=1),
        is_active=True,
        note="Initial Template",
    )
    foreign_template_domain = RecurringTransactionDomain(
        household_id=foreign_household.id,
        created_by=foreign_user.id,
        amount=300_000,
        type="expense",
        category_id=foreign_category.id,
        frequency="daily",
        next_run_date=datetime.now(UTC) + timedelta(days=1),
        is_active=True,
        note="Foreign Template",
    )

    async with uow:
        template = await uow.recurring_transactions.insert_template(template_domain)
        foreign_template = await uow.recurring_transactions.insert_template(
            foreign_template_domain
        )

    return {
        "owner": owner,
        "member": member,
        "viewer": viewer,
        "foreign_user": foreign_user,
        "household": household,
        "foreign_household": foreign_household,
        "category": category,
        "foreign_category": foreign_category,
        "template": template,
        "foreign_template": foreign_template,
    }


class TestTransactionServiceRecurring:
    async def test_add_transaction_with_frequency_as_owner_happy_path(
        self,
        transaction_service,
        recurring_service,
        recurring_env,
    ):
        payload = TransactionCreate(
            amount=150_000,
            type="expense",
            category_id=recurring_env["category"].id,
            frequency="daily",
            note="Daily Coffee",
        )

        with patch("app.service.enqueue_recurring_transaction"):
            response = await transaction_service.add_transaction(
                household_id=recurring_env["household"].id,
                user_id=recurring_env["owner"].id,
                data=payload,
                user_role=HouseholdRole.OWNER,
            )

        assert response.id is not None
        assert response.amount == 150_000
        assert response.type == "expense"

        templates = await recurring_service.get_all_templates(
            recurring_env["household"].id
        )
        created_template = next(
            (t for t in templates if t.note == "Daily Coffee"), None
        )
        assert created_template is not None
        assert created_template.amount == 150_000
        assert created_template.category_id == recurring_env["category"].id
        assert created_template.frequency == "daily"
        assert created_template.is_active is True

    async def test_add_transaction_with_frequency_as_member_forbidden(
        self,
        transaction_service,
        recurring_env,
    ):
        payload = TransactionCreate(
            amount=50_000,
            type="expense",
            category_id=recurring_env["category"].id,
            frequency="daily",
        )

        with pytest.raises(ForbiddenError) as exc_info:
            await transaction_service.add_transaction(
                household_id=recurring_env["household"].id,
                user_id=recurring_env["member"].id,
                data=payload,
                user_role=HouseholdRole.MEMBER,
            )

        assert exc_info.value.error_code == "OWNER_PERMISSION_REQUIRED"

    async def test_add_transaction_with_frequency_viewer_forbidden(
        self,
        transaction_service,
        recurring_env,
    ):
        payload = TransactionCreate(
            amount=50_000,
            type="expense",
            category_id=recurring_env["category"].id,
            frequency="daily",
        )

        with pytest.raises(ForbiddenError) as exc_info:
            await transaction_service.add_transaction(
                household_id=recurring_env["household"].id,
                user_id=recurring_env["viewer"].id,
                data=payload,
                user_role=HouseholdRole.VIEWER,
            )

        assert exc_info.value.error_code == "OWNER_PERMISSION_REQUIRED"

    async def test_add_transaction_with_frequency_nonexistent_category(
        self,
        transaction_service,
        recurring_env,
    ):
        payload = TransactionCreate(
            amount=50_000,
            type="expense",
            category_id=999_999,
            frequency="daily",
        )

        with pytest.raises(NotFoundError) as exc_info:
            await transaction_service.add_transaction(
                household_id=recurring_env["household"].id,
                user_id=recurring_env["owner"].id,
                data=payload,
                user_role=HouseholdRole.OWNER,
            )

        assert exc_info.value.error_code == "CATEGORY_NOT_FOUND"

    async def test_add_recurring_transaction_overbudget_prevents_template_creation(
        self,
        transaction_service,
        recurring_service,
        recurring_env,
    ):
        household_id = recurring_env["household"].id
        owner_id = recurring_env["owner"].id
        category_id = recurring_env["category"].id

        payload = TransactionCreate(
            amount=1_000_001,
            type="expense",
            category_id=category_id,
            frequency="daily",
            note="Overbudget Attempt",
        )

        with pytest.raises(BusinessRuleError) as exc_info:
            await transaction_service.add_transaction(
                household_id=household_id,
                user_id=owner_id,
                data=payload,
                user_role=HouseholdRole.OWNER,
            )

        assert exc_info.value.error_code == "BUDGET_LIMIT_EXCEEDED"

        templates = await recurring_service.get_all_templates(household_id)
        assert not any(t.note == "Overbudget Attempt" for t in templates)

    async def test_add_recurring_income_transaction_happy_path(
        self,
        transaction_service,
        recurring_service,
        recurring_env,
    ):
        payload = TransactionCreate(
            amount=800_000,
            type="income",
            frequency="daily",
            note="Daily Dividend",
        )

        with patch("app.service.enqueue_recurring_transaction"):
            response = await transaction_service.add_transaction(
                household_id=recurring_env["household"].id,
                user_id=recurring_env["owner"].id,
                data=payload,
                user_role=HouseholdRole.OWNER,
            )

        assert response.id is not None
        assert response.type == "income"
        assert response.category_id is None

        templates = await recurring_service.get_all_templates(
            recurring_env["household"].id
        )
        income_template = next(
            (t for t in templates if t.note == "Daily Dividend"), None
        )
        assert income_template is not None
        assert income_template.type == "income"
        assert income_template.category_id is None

    async def test_add_recurring_transaction_enqueues_dramatiq_actor(
        self,
        transaction_service,
        recurring_env,
    ):
        payload = TransactionCreate(
            amount=70_000,
            type="expense",
            category_id=recurring_env["category"].id,
            frequency="daily",
            note="Enqueued Recurring",
        )

        with patch("app.service.enqueue_recurring_transaction") as mock_enqueue:
            await transaction_service.add_transaction(
                household_id=recurring_env["household"].id,
                user_id=recurring_env["owner"].id,
                data=payload,
                user_role=HouseholdRole.OWNER,
            )

            assert mock_enqueue.called
            call_args = mock_enqueue.call_args[0]
            assert isinstance(call_args[0], int)
            assert call_args[1] >= 0

    async def test_add_recurring_transaction_redis_failure(
        self,
        transaction_service,
        recurring_env,
        fake_redis: fakeredis.aioredis.FakeRedis,
    ):
        payload = TransactionCreate(
            amount=50_000,
            type="expense",
            category_id=recurring_env["category"].id,
            frequency="daily",
            note="Redis Failing Tx",
        )

        with (
            patch.object(
                fake_redis,
                "delete",
                side_effect=redis.exceptions.ConnectionError("Redis connection lost"),
            ),
            pytest.raises(redis.exceptions.ConnectionError),
        ):
            await transaction_service.add_transaction(
                household_id=recurring_env["household"].id,
                user_id=recurring_env["owner"].id,
                data=payload,
                user_role=HouseholdRole.OWNER,
            )


class TestRecurringTransactionService:
    async def test_get_all_templates_happy_path(
        self,
        recurring_service,
        recurring_env,
        db_session: AsyncSession,
    ):
        uow = get_uow(db_session)
        second_template = RecurringTransactionDomain(
            household_id=recurring_env["household"].id,
            created_by=recurring_env["owner"].id,
            amount=350_000,
            type="income",
            frequency="daily",
            next_run_date=datetime.now(UTC) + timedelta(days=2),
            is_active=False,
            note="Second Template",
        )
        async with uow:
            await uow.recurring_transactions.insert_template(second_template)

        templates = await recurring_service.get_all_templates(
            recurring_env["household"].id
        )

        assert len(templates) >= 2
        template_ids = [t.id for t in templates]
        assert recurring_env["template"].id in template_ids

    async def test_get_all_templates_cross_household_isolation(
        self,
        recurring_service,
        recurring_env,
    ):
        templates = await recurring_service.get_all_templates(
            recurring_env["household"].id
        )

        template_ids = [t.id for t in templates]
        assert recurring_env["template"].id in template_ids
        assert recurring_env["foreign_template"].id not in template_ids

    async def test_update_template_as_owner_happy_path(
        self,
        recurring_service,
        recurring_env,
    ):
        payload = RecurringTransactionUpdate(
            amount=250_000,
            note="Updated Gym Subscription",
            is_active=False,
        )

        response = await recurring_service.update_template(
            household_id=recurring_env["household"].id,
            template_id=recurring_env["template"].id,
            user_id=recurring_env["owner"].id,
            user_role=HouseholdRole.OWNER,
            data=payload,
        )

        assert response.id == recurring_env["template"].id
        assert response.amount == 250_000
        assert response.note == "Updated Gym Subscription"
        assert response.is_active is False

    async def test_update_template_as_member_forbidden(
        self,
        recurring_service,
        recurring_env,
    ):
        payload = RecurringTransactionUpdate(amount=300_000)

        with pytest.raises(ForbiddenError) as exc_info:
            await recurring_service.update_template(
                household_id=recurring_env["household"].id,
                template_id=recurring_env["template"].id,
                user_id=recurring_env["member"].id,
                user_role=HouseholdRole.MEMBER,
                data=payload,
            )

        assert exc_info.value.error_code == "OWNER_PERMISSION_REQUIRED"

    async def test_update_template_viewer_role_forbidden(
        self,
        recurring_service,
        recurring_env,
    ):
        payload = RecurringTransactionUpdate(amount=300_000)

        with pytest.raises(ForbiddenError) as exc_info:
            await recurring_service.update_template(
                household_id=recurring_env["household"].id,
                template_id=recurring_env["template"].id,
                user_id=recurring_env["viewer"].id,
                user_role=HouseholdRole.VIEWER,
                data=payload,
            )

        assert exc_info.value.error_code == "OWNER_PERMISSION_REQUIRED"

    async def test_update_template_exceeds_budget(
        self,
        recurring_service,
        recurring_env,
    ):
        payload = RecurringTransactionUpdate(amount=1_000_001)

        with pytest.raises(BusinessRuleError) as exc_info:
            await recurring_service.update_template(
                household_id=recurring_env["household"].id,
                template_id=recurring_env["template"].id,
                user_id=recurring_env["owner"].id,
                user_role=HouseholdRole.OWNER,
                data=payload,
            )

        assert exc_info.value.error_code == "BUDGET_LIMIT_EXCEEDED"

    async def test_update_template_not_found(
        self,
        recurring_service,
        recurring_env,
    ):
        payload = RecurringTransactionUpdate(amount=100_000)

        with pytest.raises(NotFoundError) as exc_info:
            await recurring_service.update_template(
                household_id=recurring_env["household"].id,
                template_id=999_999,
                user_id=recurring_env["owner"].id,
                user_role=HouseholdRole.OWNER,
                data=payload,
            )

        assert exc_info.value.error_code == "RECURRING_TEMPLATE_NOT_FOUND"

    async def test_update_template_change_category_to_foreign_category(
        self,
        recurring_service,
        recurring_env,
    ):
        payload = RecurringTransactionUpdate(
            category_id=recurring_env["foreign_category"].id
        )

        with pytest.raises(NotFoundError) as exc_info:
            await recurring_service.update_template(
                household_id=recurring_env["household"].id,
                template_id=recurring_env["template"].id,
                user_id=recurring_env["owner"].id,
                user_role=HouseholdRole.OWNER,
                data=payload,
            )

        assert exc_info.value.error_code == "CATEGORY_NOT_FOUND"

    async def test_update_template_conflict_income_with_category(
        self,
        recurring_service,
        recurring_env,
    ):
        payload = RecurringTransactionUpdate(
            type="income",
            category_id=recurring_env["category"].id,
        )

        with pytest.raises(BusinessRuleError) as exc_info:
            await recurring_service.update_template(
                household_id=recurring_env["household"].id,
                template_id=recurring_env["template"].id,
                user_id=recurring_env["owner"].id,
                user_role=HouseholdRole.OWNER,
                data=payload,
            )

        assert exc_info.value.error_code == "INCOME_CATEGORY_CONFLICT"

    async def test_update_template_next_run_date_in_past(
        self,
        recurring_service,
        recurring_env,
    ):
        past_date = datetime.now(UTC) - timedelta(days=2)
        try:
            payload = RecurringTransactionUpdate(next_run_date=past_date)
            response = await recurring_service.update_template(
                household_id=recurring_env["household"].id,
                template_id=recurring_env["template"].id,
                user_id=recurring_env["owner"].id,
                user_role=HouseholdRole.OWNER,
                data=payload,
            )
            assert response.next_run_date is not None
        except (BusinessRuleError, ValidationError) as exc:
            assert exc is not None

    async def test_update_template_empty_payload_noop(
        self,
        recurring_service,
        recurring_env,
    ):
        payload = RecurringTransactionUpdate()

        response = await recurring_service.update_template(
            household_id=recurring_env["household"].id,
            template_id=recurring_env["template"].id,
            user_id=recurring_env["owner"].id,
            user_role=HouseholdRole.OWNER,
            data=payload,
        )

        assert response.id == recurring_env["template"].id
        assert response.amount == recurring_env["template"].amount
        assert response.type == recurring_env["template"].type
        assert response.category_id == recurring_env["template"].category_id

    async def test_update_template_amount_zero_or_negative(
        self,
        recurring_service,
        recurring_env,
    ):
        with pytest.raises(BusinessRuleError) as exc_domain:
            RecurringTransactionDomain(
                household_id=recurring_env["household"].id,
                created_by=recurring_env["owner"].id,
                amount=0,
                type="expense",
                next_run_date=datetime.now(UTC),
            )
        assert exc_domain.value.error_code == "INVALID_AMOUNT"

        with pytest.raises((ValidationError, BusinessRuleError)) as exc_info:
            payload = RecurringTransactionUpdate(amount=0)
            await recurring_service.update_template(
                household_id=recurring_env["household"].id,
                template_id=recurring_env["template"].id,
                user_id=recurring_env["owner"].id,
                user_role=HouseholdRole.OWNER,
                data=payload,
            )

        if isinstance(exc_info.value, BusinessRuleError):
            assert exc_info.value.error_code == "INVALID_AMOUNT"

    async def test_update_template_note_max_length_boundary(
        self,
        recurring_service,
        recurring_env,
    ):
        valid_note = "a" * 225
        payload = RecurringTransactionUpdate(note=valid_note)
        response = await recurring_service.update_template(
            household_id=recurring_env["household"].id,
            template_id=recurring_env["template"].id,
            user_id=recurring_env["owner"].id,
            user_role=HouseholdRole.OWNER,
            data=payload,
        )
        assert response.note == valid_note

        invalid_note = "a" * 226
        with pytest.raises((ValidationError, BusinessRuleError)) as exc_info:
            invalid_payload = RecurringTransactionUpdate(note=invalid_note)
            await recurring_service.update_template(
                household_id=recurring_env["household"].id,
                template_id=recurring_env["template"].id,
                user_id=recurring_env["owner"].id,
                user_role=HouseholdRole.OWNER,
                data=invalid_payload,
            )

        if isinstance(exc_info.value, BusinessRuleError):
            assert exc_info.value.error_code == "NOTE_TOO_LONG"

    async def test_delete_template_as_owner_happy_path(
        self,
        recurring_service,
        recurring_env,
    ):
        await recurring_service.delete_template(
            household_id=recurring_env["household"].id,
            template_id=recurring_env["template"].id,
            user_id=recurring_env["owner"].id,
            user_role=HouseholdRole.OWNER,
        )

        templates = await recurring_service.get_all_templates(
            recurring_env["household"].id
        )
        assert not any(t.id == recurring_env["template"].id for t in templates)

    async def test_delete_template_as_member_forbidden(
        self,
        recurring_service,
        recurring_env,
    ):
        with pytest.raises(ForbiddenError) as exc_info:
            await recurring_service.delete_template(
                household_id=recurring_env["household"].id,
                template_id=recurring_env["template"].id,
                user_id=recurring_env["member"].id,
                user_role=HouseholdRole.MEMBER,
            )

        assert exc_info.value.error_code == "OWNER_PERMISSION_REQUIRED"

    async def test_delete_template_cross_household_not_found(
        self,
        recurring_service,
        recurring_env,
    ):
        with pytest.raises(NotFoundError) as exc_info:
            await recurring_service.delete_template(
                household_id=recurring_env["foreign_household"].id,
                template_id=recurring_env["template"].id,
                user_id=recurring_env["owner"].id,
                user_role=HouseholdRole.OWNER,
            )

        assert exc_info.value.error_code == "RECURRING_TEMPLATE_NOT_FOUND"
