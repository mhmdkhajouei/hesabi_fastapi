import pytest

from app.db.database import (
    Budget,
    Category,
    Household,
    HouseholdRole,
    Transaction,
    User,
)
from app.dependencies import (
    get_category_repo,
    get_category_service,
    get_transaction_repo,
    get_transaction_service,
)
from app.errors.exceptions import ForbiddenError, NotFoundError
from app.schemas import (
    CategoryCreate,
    CategoryUpdate,
    TransactionCreate,
    TransactionUpdate,
)


@pytest.fixture
def category_service(db_session):
    repo = get_category_repo(db_session)
    return get_category_service(repo)


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
        budget=Budget(goal=5000),
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
    repo = get_transaction_repo(db_session)
    category_repo = get_category_repo(db_session)
    return get_transaction_service(repo, category_repo)


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
async def seed_transaction(
    db_session, seed_household, seed_user, seed_category
) -> Transaction:
    transaction = Transaction(
        amount=150_000,
        type="expense",
        household_id=seed_household.id,
        created_by=seed_user.id,
        category_id=seed_category.id,
        note="Initial grocery shopping",
    )
    db_session.add(transaction)
    await db_session.flush()
    return transaction


class TestTransactionService:
    async def test_create_expense_transaction_success(
        self, transaction_service, seed_household, seed_user, seed_category
    ):
        payload = TransactionCreate(
            amount=50_000,
            type="expense",
            category_id=seed_category.id,
            note="Fruits",
        )

        response = await transaction_service.add_transaction(
            household_id=seed_household.id,
            user_id=seed_user.id,
            data=payload,
        )

        assert response.id is not None
        assert response.amount == 50_000
        assert response.category_id == seed_category.id
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
