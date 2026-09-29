from datetime import UTC, datetime, timedelta

import pytest

from app.domain_models import CategoryDomain, TransactionDomain
from app.errors.exceptions import BusinessRuleError


class TestCategoryDomain:
    def test_create_category_happy_path(self):
        name = "Groceries"
        budget_goal = 5000000
        houshold_id = 1

        category = CategoryDomain(
            name=name, budget_goal=budget_goal, household_id=houshold_id
        )

        assert category.name == "Groceries"
        assert category.budget_goal == 5000000
        assert category.household_id == 1

    @pytest.mark.parametrize("name_len", [19, 20])
    def test_valid_name_length(self, name_len):
        name = "A" * name_len
        category = CategoryDomain(name=name, budget_goal=1000, household_id=1)
        assert len(category.name) == name_len

    @pytest.mark.parametrize("invalid_name_len", [21, 50])
    def test_invalid_name_length(self, invalid_name_len):
        name = "A" * invalid_name_len
        with pytest.raises(BusinessRuleError) as exc_info:
            CategoryDomain(name=name, budget_goal=5000, household_id=2)
        assert exc_info.value.error_code == "CATEGORY_NAME_TOO_LONG"

    @pytest.mark.parametrize("empty_name", [None, "", " ", "\t\n"])
    def test_empty_name(self, empty_name):
        with pytest.raises(BusinessRuleError) as exc_info:
            CategoryDomain(name=empty_name, budget_goal=5000, household_id=2)
        assert exc_info.value.error_code == "INVALID_CATEGORY_NAME"

    def test_name_stripping_whitespace(self):
        name = "    Groceries    "
        category = CategoryDomain(name=name, budget_goal=1000, household_id=1)
        assert category.name == "Groceries"

    def test_name_stripping_valid_length(self):
        name = "     " + ("A" * 15) + "     "
        category = CategoryDomain(name=name, budget_goal=1000, household_id=1)
        assert len(category.name) == 15

    @pytest.mark.parametrize("unicode_name", ["خواربار و خوراکی", "اجاره خانه 🏠"])
    def test_name_with_unicode(self, unicode_name):
        category = CategoryDomain(name=unicode_name, budget_goal=1000, household_id=1)
        assert category.name == unicode_name

    @pytest.mark.parametrize("invalid_budget_goal", [-1, 0, None])
    def test_invalid_budget_goal(self, invalid_budget_goal):
        with pytest.raises(BusinessRuleError) as exc_info:
            CategoryDomain(name="Ali", budget_goal=invalid_budget_goal, household_id=1)
        assert exc_info.value.error_code == "INVALID_BUDGET_GOAL"

    def test_invalid_big_budget_goal(self):
        with pytest.raises(BusinessRuleError) as exc_info:
            CategoryDomain(name="Ali", budget_goal=-5000000, household_id=1)
        assert exc_info.value.error_code == "INVALID_BUDGET_GOAL"

    def test_valid_big_budget_goal(self):
        category = CategoryDomain(name="Ali", budget_goal=500_000_000, household_id=1)
        assert category.budget_goal == 500000000

    @pytest.mark.parametrize("invalid_hh_id", [-1, 0, None])
    def test_invalid_hh_id(self, invalid_hh_id):
        with pytest.raises(BusinessRuleError) as exc_info:
            CategoryDomain(name="Ali", budget_goal=5000, household_id=invalid_hh_id)
        assert exc_info.value.error_code == "INVALID_HOUSEHOLD_ID"


class TestTransactionDomain:
    def test_create_transaction_happy_path(self):
        now = datetime.now(UTC)
        transaction = TransactionDomain(
            amount=50000,
            household_id=1,
            created_by=2,
            type="expense",
            date=now,
            note="Lunch",
            category_id=10,
        )

        assert transaction.amount == 50000
        assert transaction.household_id == 1
        assert transaction.created_by == 2
        assert transaction.type == "expense"
        assert transaction.date == now
        assert transaction.note == "Lunch"
        assert transaction.category_id == 10

    def test_create_income_transaction_without_category_happy_path(self):
        transaction = TransactionDomain(
            amount=1000000,
            household_id=1,
            created_by=2,
            type="income",
            category_id=None,
        )

        assert transaction.type == "income"
        assert transaction.category_id is None

    @pytest.mark.parametrize("invalid_household_id", [-1, 0, None])
    def test_invalid_household_id(self, invalid_household_id):
        with pytest.raises(BusinessRuleError) as exc_info:
            TransactionDomain(
                amount=1000,
                household_id=invalid_household_id,
                created_by=1,
                type="expense",
            )
        assert exc_info.value.error_code == "INVALID_HOUSEHOLD_ID"

    @pytest.mark.parametrize("invalid_user_id", [-1, 0, None])
    def test_invalid_created_by(self, invalid_user_id):
        with pytest.raises(BusinessRuleError) as exc_info:
            TransactionDomain(
                amount=1000,
                household_id=1,
                created_by=invalid_user_id,
                type="expense",
            )
        assert exc_info.value.error_code == "INVALID_USER_ID"

    @pytest.mark.parametrize("invalid_amount", [-1, 0, None])
    def test_invalid_amount(self, invalid_amount):
        with pytest.raises(BusinessRuleError) as exc_info:
            TransactionDomain(
                amount=invalid_amount,
                household_id=1,
                created_by=1,
                type="expense",
            )
        assert exc_info.value.error_code == "INVALID_AMOUNT"

    def test_income_with_category_conflict(self):
        with pytest.raises(BusinessRuleError) as exc_info:
            TransactionDomain(
                amount=1000,
                household_id=1,
                created_by=1,
                type="income",
                category_id=5,
            )
        assert exc_info.value.error_code == "INCOME_CATEGORY_CONFLICT"

    def test_future_date_rejected(self):
        future_date = datetime.now(UTC) + timedelta(days=1)
        with pytest.raises(BusinessRuleError) as exc_info:
            TransactionDomain(
                amount=1000,
                household_id=1,
                created_by=1,
                type="expense",
                date=future_date,
            )
        assert exc_info.value.error_code == "FUTURE_DATE_NOT_ALLOWED"

    def test_naive_datetime_converted_to_utc(self):
        naive_date = datetime(2025, 1, 1, 12, 0, 0)  # noqa: DTZ001
        transaction = TransactionDomain(
            amount=1000,
            household_id=1,
            created_by=1,
            type="expense",
            date=naive_date,
        )
        assert transaction.date is not None
        assert transaction.date.tzinfo == UTC
        assert transaction.date == naive_date.replace(tzinfo=UTC)

    @pytest.mark.parametrize("note_len", [224, 225])
    def test_valid_note_length(self, note_len):
        note = "N" * note_len
        transaction = TransactionDomain(
            amount=1000,
            household_id=1,
            created_by=1,
            type="expense",
            note=note,
        )
        assert transaction.note is not None
        assert len(transaction.note) == note_len

    @pytest.mark.parametrize("invalid_note_len", [226, 300])
    def test_invalid_note_length(self, invalid_note_len):
        note = "N" * invalid_note_len
        with pytest.raises(BusinessRuleError) as exc_info:
            TransactionDomain(
                amount=1000,
                household_id=1,
                created_by=1,
                type="expense",
                note=note,
            )
        assert exc_info.value.error_code == "NOTE_TOO_LONG"

    def test_note_stripping_whitespace(self):
        transaction = TransactionDomain(
            amount=1000,
            household_id=1,
            created_by=1,
            type="expense",
            note="   Dinner with family   ",
        )
        assert transaction.note == "Dinner with family"

    @pytest.mark.parametrize("empty_note", ["", "   ", "\t\n"])
    def test_empty_or_whitespace_note_converted_to_none(self, empty_note):
        transaction = TransactionDomain(
            amount=1000,
            household_id=1,
            created_by=1,
            type="expense",
            note=empty_note,
        )
        assert transaction.note is None
