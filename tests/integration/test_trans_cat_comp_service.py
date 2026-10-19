import asyncio

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.db.database import (
    Budget,
    Category,
    Household,
    HouseholdRole,
    Transaction,
    User,
)
from app.dependencies import (
    get_category_service,
    get_compute_service,
    get_transaction_service,
    get_uow,
)
from app.errors.exceptions import BusinessRuleError, ForbiddenError, NotFoundError
from app.schemas import (
    CategoryCreate,
    CategoryUpdate,
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)


@pytest.fixture
def category_service(db_session):
    uow = get_uow(db_session)
    return get_category_service(uow)


@pytest.fixture
async def seed_household(db_session) -> Household:
    household = Household(name="Our Family")
    db_session.add(household)
    await db_session.flush()
    return household


@pytest.fixture
async def seed_category(db_session, seed_household) -> Category:
    category = Category(
        name="Groceries",
        budget=Budget(goal=1000000),
        household_id=seed_household.id,
    )
    db_session.add(category)
    await db_session.flush()
    return category


class TestCategoryService:
    async def test_create_category_success(self, category_service, seed_household):
        payload = CategoryCreate(name="Foods", budget_goal=5000)

        response = await category_service.add_category(
            household_id=seed_household.id,
            category=payload,
        )

        assert response.id is not None
        assert response.name == "Foods"
        assert response.budget_goal == 5000

    async def test_edit_category_full_update(self, category_service, seed_category):
        payload = CategoryUpdate(name="Clothes", budget_goal=4000)

        response = await category_service.edit_category(
            seed_category.household_id,
            seed_category.id,
            payload,
        )

        assert response.id == seed_category.id
        assert response.name == "Clothes"
        assert response.budget_goal == 4000

    async def test_edit_category_partial_update(self, category_service, seed_category):
        payload = CategoryUpdate(name="Clothes")

        response = await category_service.edit_category(
            seed_category.household_id,
            seed_category.id,
            payload,
        )

        assert response.id == seed_category.id
        assert response.name == "Clothes"

    async def test_edit_category_not_found(self, category_service, seed_category):

        payload = CategoryUpdate(name="Clothes")
        with pytest.raises(NotFoundError) as exc_info:
            await category_service.edit_category(
                seed_category.household_id,
                999_999,
                payload,
            )
        assert exc_info.value.error_code == "CATEGORY_NOT_FOUND"

    async def test_delete_category_success(
        self, category_service, seed_category, seed_household
    ):
        await category_service.delete_category(
            seed_category.household_id,
            seed_category.id,
        )

    async def test_delete_category_not_found(
        self, category_service, seed_category, seed_household
    ):

        with pytest.raises(NotFoundError) as exc_info:
            await category_service.delete_category(
                seed_household.id,
                999_999,
            )

        assert exc_info.value.error_code == "CATEGORY_NOT_FOUND"

    async def test_get_category_success(self, category_service, seed_category):
        category = await category_service.get_category(
            seed_category.household_id,
            seed_category.id,
        )

        assert category.id == seed_category.id
        assert category.name == seed_category.name
        assert category.budget_goal == seed_category.budget_goal

    async def test_get_category_not_found(self, category_service, seed_category):
        with pytest.raises(NotFoundError) as exc_info:
            await category_service.get_category(
                seed_category.household_id,
                999_999,
            )
        assert exc_info.value.error_code == "CATEGORY_NOT_FOUND"

    async def test_get_all_categories_success(
        self, category_service, seed_household, db_session
    ):

        cat_1 = Category(
            household_id=seed_household.id, name="Food", budget=Budget(goal=5000)
        )
        cat_2 = Category(
            household_id=seed_household.id,
            name="Clothes",
            budget=Budget(goal=2000),
        )

        db_session.add_all([cat_1, cat_2])
        await db_session.flush()

        results = await category_service.get_all_categories(seed_household.id)

        assert len(results) == 2
        category_ids = [c.id for c in results]
        assert cat_1.id in category_ids
        assert cat_2.id in category_ids


"""
----------------------------------
Transactions 
----------------------------------
"""


@pytest.fixture
def transaction_service(db_session):
    uow = get_uow(db_session)
    return get_transaction_service(uow)


DUMMY_SECURE_HASH = "$2b$12$e86gOzU4mO8hE7gYQx3x8.0yY2B5V3d3gS4v2X6M0F2k6P1q9e7W2"


@pytest.fixture
async def seed_user(db_session) -> User:
    user = User(
        email="owner@hesabi.com",
        password_hash=DUMMY_SECURE_HASH,
        name="Owner User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def seed_member_user(db_session) -> User:
    user = User(
        email="member@hesabi.com",
        password_hash=DUMMY_SECURE_HASH,
        name="Member User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def seed_category_2(db_session, seed_household) -> Category:
    category = Category(
        name="HipHop",
        budget=Budget(goal=1000000),
        household_id=seed_household.id,
    )
    db_session.add(category)
    await db_session.flush()
    return category


@pytest.fixture
async def seed_transaction(
    db_session, seed_household, seed_user, seed_category_2
) -> Transaction:
    transaction = Transaction(
        amount=100000,
        type="expense",
        household_id=seed_household.id,
        created_by=seed_user.id,
        category_id=seed_category_2.id,
        note="Initial grocery shopping",
    )
    db_session.add(transaction)
    await db_session.flush()
    return transaction


class TestTransactionService:
    async def test_create_expense_transaction_success(
        self, transaction_service, seed_household, seed_user, seed_category_2
    ):
        payload = TransactionCreate(
            amount=50_000,
            type="expense",
            category_id=seed_category_2.id,
            note="Fruits",
        )

        response = await transaction_service.add_transaction(
            household_id=seed_household.id,
            user_id=seed_user.id,
            data=payload,
        )

        assert response.id is not None
        assert response.amount == 50_000
        assert response.category_id == seed_category_2.id
        assert response.type == "expense"
        assert response.note == "Fruits"

    async def test_create_income_transaction_success(
        self, transaction_service, seed_household, seed_user
    ):
        payload = TransactionCreate(
            amount=1_000_000,
            type="income",
            note="Bonus",
        )

        response = await transaction_service.add_transaction(
            household_id=seed_household.id,
            user_id=seed_user.id,
            data=payload,
        )

        assert response.id is not None
        assert response.amount == 1_000_000
        assert response.type == "income"
        assert response.category_id is None

    async def test_create_transaction_category_not_found(
        self, transaction_service, seed_household, seed_user
    ):
        payload = TransactionCreate(
            amount=50_000,
            type="expense",
            category_id=999_999,
        )

        with pytest.raises(NotFoundError) as exc_info:
            await transaction_service.add_transaction(
                household_id=seed_household.id,
                user_id=seed_user.id,
                data=payload,
            )

        assert exc_info.value.error_code == "CATEGORY_NOT_FOUND"

    async def test_create_expense_transaction_exact_limit(
        self, transaction_service, seed_household, seed_user, seed_category_2
    ):
        payload = TransactionCreate(
            amount=1000000,
            type="expense",
            category_id=seed_category_2.id,
        )
        response = await transaction_service.add_transaction(
            household_id=seed_household.id,
            user_id=seed_user.id,
            data=payload,
        )
        assert response.amount == 1000000

    async def test_create_expense_transaction_overbudget_fails(
        self, transaction_service, seed_user, seed_category_2, seed_household
    ):
        payload = TransactionCreate(
            amount=1000001,
            type="expense",
            category_id=seed_category_2.id,
        )
        with pytest.raises(BusinessRuleError) as exc_info:
            await transaction_service.add_transaction(
                household_id=seed_household.id,
                user_id=seed_user.id,
                data=payload,
            )
        assert exc_info.value.error_code == "BUDGET_LIMIT_EXCEEDED"

    async def test_edit_transaction_success(
        self, transaction_service, seed_transaction, seed_user
    ):
        payload = TransactionUpdate(amount=200_000, note="Updated note")

        response = await transaction_service.edit_transaction(
            household_id=seed_transaction.household_id,
            transaction_id=seed_transaction.id,
            user_id=seed_user.id,
            user_role=HouseholdRole.OWNER,
            data=payload,
        )

        assert response.id == seed_transaction.id
        assert response.amount == 200_000
        assert response.note == "Updated note"

    async def test_edit_transaction_same_category_overbudget_fails(
        self, transaction_service, seed_transaction, seed_user
    ):
        payload = TransactionUpdate(amount=1000001)

        with pytest.raises(BusinessRuleError) as exc_info:
            await transaction_service.edit_transaction(
                household_id=seed_transaction.household_id,
                transaction_id=seed_transaction.id,
                user_id=seed_user.id,
                user_role=HouseholdRole.OWNER,
                data=payload,
            )
        assert exc_info.value.error_code == "BUDGET_LIMIT_EXCEEDED"

    async def test_edit_transaction_success_change_category_exact_limit(
        self, transaction_service, seed_transaction, seed_user, seed_category
    ):
        payload = TransactionUpdate(
            amount=900000, category_id=seed_category.id, note="Updated note"
        )

        response = await transaction_service.edit_transaction(
            household_id=seed_transaction.household_id,
            transaction_id=seed_transaction.id,
            user_id=seed_user.id,
            user_role=HouseholdRole.OWNER,
            data=payload,
        )

        assert response.id == seed_transaction.id
        assert response.amount == 900000
        assert response.note == "Updated note"

    async def test_edit_transaction_change_category_overbudget_fails(
        self, transaction_service, seed_transaction, seed_user, seed_category
    ):
        payload = TransactionUpdate(amount=1000001, category_id=seed_category.id)

        with pytest.raises(BusinessRuleError) as exc_info:
            await transaction_service.edit_transaction(
                household_id=seed_transaction.household_id,
                transaction_id=seed_transaction.id,
                user_id=seed_user.id,
                user_role=HouseholdRole.OWNER,
                data=payload,
            )
        assert exc_info.value.error_code == "BUDGET_LIMIT_EXCEEDED"

    async def test_edit_transaction_change_type_to_income_removes_category(
        self, transaction_service, seed_transaction, seed_user
    ):
        payload = TransactionUpdate(type="income")

        response = await transaction_service.edit_transaction(
            household_id=seed_transaction.household_id,
            transaction_id=seed_transaction.id,
            user_id=seed_user.id,
            user_role=HouseholdRole.OWNER,
            data=payload,
        )

        assert response.type == "income"
        assert response.category_id is None

    async def test_edit_transaction_invalid_category_not_found(
        self, transaction_service, seed_transaction, seed_user
    ):
        payload = TransactionUpdate(category_id=999_999)

        with pytest.raises(NotFoundError) as exc_info:
            await transaction_service.edit_transaction(
                household_id=seed_transaction.household_id,
                transaction_id=seed_transaction.id,
                user_id=seed_user.id,
                user_role=HouseholdRole.OWNER,
                data=payload,
            )

        assert exc_info.value.error_code == "CATEGORY_NOT_FOUND"

    async def test_edit_transaction_member_forbidden_for_other_user(
        self, transaction_service, seed_transaction, seed_member_user
    ):
        payload = TransactionUpdate(amount=300_000)

        with pytest.raises(ForbiddenError) as exc_info:
            await transaction_service.edit_transaction(
                household_id=seed_transaction.household_id,
                transaction_id=seed_transaction.id,
                user_id=seed_member_user.id,
                user_role=HouseholdRole.MEMBER,
                data=payload,
            )

        assert exc_info.value.error_code == "INSUFFICIENT_PERMISSIONS"

    async def test_edit_transaction_not_found(
        self, transaction_service, seed_household, seed_user
    ):
        payload = TransactionUpdate(amount=500_000)

        with pytest.raises(NotFoundError) as exc_info:
            await transaction_service.edit_transaction(
                household_id=seed_household.id,
                transaction_id=999_999,
                user_id=seed_user.id,
                user_role=HouseholdRole.OWNER,
                data=payload,
            )

        assert exc_info.value.error_code == "TRANSACTION_NOT_FOUND"

    async def test_delete_transaction_success(
        self, transaction_service, seed_transaction, seed_user
    ):
        await transaction_service.delete_transaction(
            household_id=seed_transaction.household_id,
            transaction_id=seed_transaction.id,
            user_id=seed_user.id,
            user_role=HouseholdRole.OWNER,
        )

        with pytest.raises(NotFoundError) as exc_info:
            await transaction_service.get_transaction(
                household_id=seed_transaction.household_id,
                transaction_id=seed_transaction.id,
            )

        assert exc_info.value.error_code == "TRANSACTION_NOT_FOUND"

    async def test_delete_transaction_member_forbidden_for_other_user(
        self, transaction_service, seed_transaction, seed_member_user
    ):
        with pytest.raises(ForbiddenError) as exc_info:
            await transaction_service.delete_transaction(
                household_id=seed_transaction.household_id,
                transaction_id=seed_transaction.id,
                user_id=seed_member_user.id,
                user_role=HouseholdRole.MEMBER,
            )

        assert exc_info.value.error_code == "INSUFFICIENT_PERMISSIONS"

    async def test_delete_transaction_not_found(
        self, transaction_service, seed_household, seed_user
    ):
        with pytest.raises(NotFoundError) as exc_info:
            await transaction_service.delete_transaction(
                household_id=seed_household.id,
                transaction_id=999_999,
                user_id=seed_user.id,
                user_role=HouseholdRole.OWNER,
            )

        assert exc_info.value.error_code == "TRANSACTION_NOT_FOUND"

    async def test_get_transaction_success(self, transaction_service, seed_transaction):
        response = await transaction_service.get_transaction(
            household_id=seed_transaction.household_id,
            transaction_id=seed_transaction.id,
        )

        assert response.id == seed_transaction.id
        assert response.amount == seed_transaction.amount
        assert response.type == seed_transaction.type

    async def test_get_transaction_not_found(self, transaction_service, seed_household):
        with pytest.raises(NotFoundError) as exc_info:
            await transaction_service.get_transaction(
                household_id=seed_household.id,
                transaction_id=999_999,
            )

        assert exc_info.value.error_code == "TRANSACTION_NOT_FOUND"

    async def test_get_all_transactions_success(
        self, transaction_service, seed_household, seed_user, db_session
    ):
        tx_1 = Transaction(
            amount=20_000,
            type="expense",
            household_id=seed_household.id,
            created_by=seed_user.id,
        )
        tx_2 = Transaction(
            amount=80_000,
            type="income",
            household_id=seed_household.id,
            created_by=seed_user.id,
        )

        db_session.add_all([tx_1, tx_2])
        await db_session.flush()

        results = await transaction_service.get_all_transactions(seed_household.id)

        assert len(results) >= 2
        tx_ids = [t.id for t in results]
        assert tx_1.id in tx_ids
        assert tx_2.id in tx_ids

    async def test_concurrent_transaction_pessimistic_lock_two_users(
        self, test_engine: AsyncEngine
    ):
        try:
            session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
            async with session_factory() as session:
                household = Household(name="Concurrency Family")
                user_a = User(
                    email="user_a@hesabi.com",
                    password_hash=DUMMY_SECURE_HASH,
                    name="User A",
                    is_active=True,
                )
                user_b = User(
                    email="user_b@hesabi.com",
                    password_hash=DUMMY_SECURE_HASH,
                    name="User a",
                    is_active=True,
                )

                session.add_all([household, user_a, user_b])
                await session.flush()

                category = Category(
                    name="LockedCategory",
                    budget=Budget(goal=1000000),
                    household_id=household.id,
                )

                session.add(category)
                await session.commit()

                household_id = household.id
                user_a_id = user_a.id
                user_b_id = user_b.id
                category_id = category.id

                async def submit_expense(caller_user_id: int) -> TransactionResponse:
                    async with session_factory() as session:
                        uow = get_uow(session)
                        async with uow:
                            service = get_transaction_service(uow)
                            payload = TransactionCreate(
                                amount=500_000, type="expense", category_id=category_id
                            )
                            return await service.add_transaction(
                                household_id=household_id,
                                user_id=caller_user_id,
                                data=payload,
                            )

                results = await asyncio.gather(
                    submit_expense(user_a_id),
                    submit_expense(user_b_id),
                    return_exceptions=True,
                )

                successes = [r for r in results if isinstance(r, TransactionResponse)]
                errors = [r for r in results if isinstance(r, Exception)]

                assert len(successes) == 2
                assert len(errors) == 0
                assert successes[0].amount == 500000
                assert successes[1].amount == 500000

                async with session_factory() as session:
                    uow = get_uow(session)
                    async with uow:
                        spent = await uow.compute.get_category_total_spent(
                            household_id=household_id,
                            category_id=category_id,
                        )
                        assert spent == 1000000
        finally:
            async with test_engine.begin() as conn:
                await conn.execute(
                    text(
                        "TRUNCATE TABLE transactions, budgets, categories,"
                        "household_members, household, users RESTART IDENTITY CASCADE"
                    )
                )

    async def test_concurrent_transaction_overbudget_pessimistic_lock_two_users(
        self, test_engine: AsyncEngine
    ):
        try:
            session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
            async with session_factory() as session:
                household = Household(name="Concurrency Family")
                user_a = User(
                    email="user_a_over@hesabi.com",
                    password_hash=DUMMY_SECURE_HASH,
                    name="User A",
                    is_active=True,
                )
                user_b = User(
                    email="user_b_over@hesabi.com",
                    password_hash=DUMMY_SECURE_HASH,
                    name="User a",
                    is_active=True,
                )

                session.add_all([household, user_a, user_b])
                await session.flush()

                category = Category(
                    name="LockedCategory",
                    budget=Budget(goal=1000000),
                    household_id=household.id,
                )

                session.add(category)
                await session.commit()

                household_id = household.id
                user_a_id = user_a.id
                user_b_id = user_b.id
                category_id = category.id

                async def submit_expense(caller_user_id: int) -> TransactionResponse:
                    async with session_factory() as session:
                        uow = get_uow(session)
                        async with uow:
                            service = get_transaction_service(uow)
                            payload = TransactionCreate(
                                amount=600_000, type="expense", category_id=category_id
                            )
                            return await service.add_transaction(
                                household_id=household_id,
                                user_id=caller_user_id,
                                data=payload,
                            )

                results = await asyncio.gather(
                    submit_expense(user_a_id),
                    submit_expense(user_b_id),
                    return_exceptions=True,
                )

                successes = [r for r in results if isinstance(r, TransactionResponse)]
                errors = [r for r in results if isinstance(r, BusinessRuleError)]

                assert len(successes) == 1
                assert len(errors) == 1
                assert errors[0].error_code == "BUDGET_LIMIT_EXCEEDED"

                async with session_factory() as session:
                    uow = get_uow(session)
                    async with uow:
                        spent = await uow.compute.get_category_total_spent(
                            household_id=household_id,
                            category_id=category_id,
                        )
                        assert spent == 600000
        finally:
            async with test_engine.begin() as conn:
                await conn.execute(
                    text(
                        "TRUNCATE TABLE transactions, budgets, categories, "
                        "household_members, household, users RESTART IDENTITY CASCADE"
                    )
                )


"""
--------------------------------
Compute
--------------------------------
"""


@pytest.fixture
def compute_service(db_session):
    uow = get_uow(db_session)
    return get_compute_service(uow)


class TestComputeService:
    async def test_get_financial_summary_empty(self, compute_service, seed_household):
        summary = await compute_service.get_financial_summary(seed_household.id)

        assert summary["income"] == 0
        assert summary["expense"] == 0
        assert summary["total"] == 0

    async def test_get_financial_summary_multiple_transactions_and_isolation(
        self, compute_service, seed_household, seed_user, db_session
    ):
        other_household = Household(name="Other Family")
        db_session.add(other_household)
        await db_session.flush()

        txs = [
            Transaction(
                amount=300_000,
                type="income",
                household_id=seed_household.id,
                created_by=seed_user.id,
            ),
            Transaction(
                amount=200_000,
                type="income",
                household_id=seed_household.id,
                created_by=seed_user.id,
            ),
            Transaction(
                amount=50_000,
                type="expense",
                household_id=seed_household.id,
                created_by=seed_user.id,
            ),
            Transaction(
                amount=70_000,
                type="expense",
                household_id=seed_household.id,
                created_by=seed_user.id,
            ),
            Transaction(
                amount=999_999,
                type="income",
                household_id=other_household.id,
                created_by=seed_user.id,
            ),
        ]
        db_session.add_all(txs)
        await db_session.flush()

        summary = await compute_service.get_financial_summary(seed_household.id)

        assert summary["income"] == 500_000
        assert summary["expense"] == 120_000
        assert summary["total"] == 380_000

    async def test_category_balance_multiple_transactions_and_overbudget(
        self,
        compute_service,
        seed_household,
        seed_user,
        seed_category,
        db_session,
    ):
        other_category = Category(
            name="Utilities",
            budget=Budget(goal=2_000),
            household_id=seed_household.id,
        )
        db_session.add(other_category)
        await db_session.flush()

        txs = [
            Transaction(
                amount=2_000,
                type="expense",
                household_id=seed_household.id,
                category_id=seed_category.id,
                created_by=seed_user.id,
            ),
            Transaction(
                amount=4_000,
                type="expense",
                household_id=seed_household.id,
                category_id=seed_category.id,
                created_by=seed_user.id,
            ),
            Transaction(
                amount=1_000,
                type="expense",
                household_id=seed_household.id,
                category_id=other_category.id,
                created_by=seed_user.id,
            ),
        ]
        db_session.add_all(txs)
        await db_session.flush()

        result = await compute_service.category_balance(
            household_id=seed_household.id, category_id=seed_category.id
        )

        assert result["name"] == seed_category.name
        assert result["budget_goal"] == seed_category.budget.goal
        assert result["spent"] == 6000
        assert result["remaining"] == 994000

    async def test_category_balance_not_found(self, compute_service, seed_household):
        with pytest.raises(NotFoundError) as exc_info:
            await compute_service.category_balance(
                household_id=seed_household.id, category_id=999_999
            )

        assert exc_info.value.error_code == "CATEGORY_NOT_FOUND"

    async def test_categories_balance_success(
        self, compute_service, seed_household, seed_user, db_session
    ):
        cat_1 = Category(
            household_id=seed_household.id,
            name="Supermarket",
            budget=Budget(goal=10_000),
        )
        cat_2 = Category(
            household_id=seed_household.id,
            name="Gym",
            budget=Budget(goal=20_000),
        )
        db_session.add_all([cat_1, cat_2])
        await db_session.flush()

        tx = Transaction(
            amount=4_000,
            type="expense",
            household_id=seed_household.id,
            category_id=cat_1.id,
            created_by=seed_user.id,
        )
        db_session.add(tx)
        await db_session.flush()

        results = await compute_service.categories_balance(seed_household.id)

        cat_1_res = next((r for r in results if r["name"] == "Supermarket"), None)
        cat_2_res = next((r for r in results if r["name"] == "Gym"), None)

        assert cat_1_res is not None
        assert cat_1_res["budget_goal"] == 10_000
        assert cat_1_res["spent"] == 4_000
        assert cat_1_res["remaining"] == 6_000

        assert cat_2_res is not None
        assert cat_2_res["budget_goal"] == 20_000
        assert cat_2_res["spent"] == 0
        assert cat_2_res["remaining"] == 20_000
