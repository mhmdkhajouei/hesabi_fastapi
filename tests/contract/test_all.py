from datetime import UTC, datetime

import pytest
from openapi_spec_validator import validate
from pydantic import ValidationError

from app.main import app
from app.schemas import (
    CategoryBalanceResponse,
    CategoryCreate,
    CategoryUpdate,
    FinancialSummaryResponse,
    TokenPayload,
    TokenRefreshRequest,
    TransactionCreate,
    TransactionResponse,
    UserRegister,
)


def test_openapi_contract_validity():
    schema = app.openapi()
    validate(schema)


class TestCategoryContract:
    def test_category_create_happy_path(self):
        cat = CategoryCreate(name="Groceries", budget_goal=500_000)
        assert cat.name == "Groceries"
        assert cat.budget_goal == 500_000

    @pytest.mark.parametrize(
        "name,goal",
        [
            ("A", 1),
            ("A" * 20, 100_000_000_000),
        ],
    )
    def test_category_create_boundaries(self, name: str, goal: int):
        cat = CategoryCreate(name=name, budget_goal=goal)
        assert cat.name == name
        assert cat.budget_goal == goal

    def test_category_create_whitespace_stripping(self):
        cat = CategoryCreate(name="   Healthcare   ", budget_goal=100_000)
        assert cat.name == "Healthcare"

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "",
            "   ",
            "A" * 21,
        ],
    )
    def test_category_create_invalid_name(self, invalid_name: str):
        with pytest.raises(ValidationError) as exc:
            CategoryCreate(name=invalid_name, budget_goal=500_000)
        assert "name" in str(exc.value)

    @pytest.mark.parametrize("invalid_goal", [0, -1, -500_000])
    def test_category_create_invalid_budget_goal(self, invalid_goal: int):
        with pytest.raises(ValidationError) as exc:
            CategoryCreate(name="Utilities", budget_goal=invalid_goal)
        assert "budget_goal" in str(exc.value)

    def test_category_update_partial_happy_path(self):
        update_name_only = CategoryUpdate(name="Gym")
        assert update_name_only.name == "Gym"
        assert update_name_only.budget_goal is None

        update_goal_only = CategoryUpdate(budget_goal=200_000)
        assert update_goal_only.name is None
        assert update_goal_only.budget_goal == 200_000

        update_empty = CategoryUpdate()
        assert update_empty.name is None
        assert update_empty.budget_goal is None


class TestTransactionContract:
    def test_transaction_create_happy_path(self):
        tx = TransactionCreate(
            amount=150_000,
            type="expense",
            note="Grocery bill",
            category_id=5,
        )
        assert tx.amount == 150_000
        assert tx.type == "expense"
        assert tx.category_id == 5

    def test_transaction_income_without_category(self):
        tx = TransactionCreate(
            amount=2_000_000,
            type="income",
            category_id=None,
        )
        assert tx.type == "income"
        assert tx.category_id is None

    @pytest.mark.parametrize("amount", [1, 10_000_000_000])
    def test_transaction_amount_boundaries(self, amount: int):
        tx = TransactionCreate(amount=amount, type="income")
        assert tx.amount == amount

    def test_transaction_note_boundary_edge_cases(self):
        valid_note = "N" * 225
        tx = TransactionCreate(amount=1000, type="expense", note=valid_note)
        assert tx.note == valid_note

        invalid_note = "N" * 226
        with pytest.raises(ValidationError) as exc:
            TransactionCreate(amount=1000, type="expense", note=invalid_note)
        assert "note" in str(exc.value)

    @pytest.mark.parametrize("invalid_amount", [0, -1, -100_000])
    def test_transaction_invalid_amount(self, invalid_amount: int):
        with pytest.raises(ValidationError) as exc:
            TransactionCreate(amount=invalid_amount, type="income")
        assert "amount" in str(exc.value)

    @pytest.mark.parametrize("invalid_type", ["transfer", "UNKNOWN", ""])
    def test_transaction_invalid_type(self, invalid_type: str):
        with pytest.raises(ValidationError) as exc:
            TransactionCreate(amount=1000, type=invalid_type)
        assert "type" in str(exc.value)

    @pytest.mark.parametrize("invalid_cat_id", [0, -5])
    def test_transaction_invalid_category_id(self, invalid_cat_id: int):
        with pytest.raises(ValidationError) as exc:
            TransactionCreate(amount=1000, type="expense", category_id=invalid_cat_id)
        assert "category_id" in str(exc.value)

    def test_transaction_response_defaults_and_datetime(self):
        now = datetime.now(UTC)
        res = TransactionResponse(
            id=1,
            amount=50_000,
            type="expense",
            date=now,
        )
        assert res.currency == "TOMAN"
        assert res.date == now


class TestUserAndAuthContract:
    def test_user_register_happy_path(self):
        user = UserRegister(
            email="Valid.User@Hesabi.COM",
            name="Mohammad Javad",
            password="StrongPassword123!",
        )
        assert user.email == "valid.user@hesabi.com"
        assert user.name == "Mohammad Javad"

    def test_user_register_whitespace_stripping(self):
        user = UserRegister(
            email="   whitespace@hesabi.com   ",
            name="   Clean Name   ",
            password="StrongPassword123!",
        )
        assert user.email == "whitespace@hesabi.com"
        assert user.name == "Clean Name"

    @pytest.mark.parametrize(
        "invalid_email",
        [
            "not-an-email",
            "@missingusername.com",
            "username@.com",
            "",
        ],
    )
    def test_user_register_invalid_email(self, invalid_email: str):
        with pytest.raises(ValidationError) as exc:
            UserRegister(
                email=invalid_email,
                password="StrongPassword123!",
            )
        assert "email" in str(exc.value)

    @pytest.mark.parametrize(
        "weak_password",
        [
            "short1!",
            "OnlyLettersNoDigits!",
            "1234567890!a",
            "alllowercase123!",
            "ALLUPPERCASE123!",
            "NoSpecialCharacter123",
            "A" * 129 + "1!",
        ],
    )
    def test_user_register_password_policies(self, weak_password: str):
        with pytest.raises(ValidationError) as exc:
            UserRegister(
                email="secure@hesabi.com",
                password=weak_password,
            )
        assert "password" in str(exc.value)

    def test_user_name_boundary(self):
        valid_name = "N" * 150
        user = UserRegister(
            email="boundary@hesabi.com",
            name=valid_name,
            password="StrongPassword123!",
        )
        assert user.name == valid_name

        invalid_name = "N" * 151
        with pytest.raises(ValidationError) as exc:
            UserRegister(
                email="boundary@hesabi.com",
                name=invalid_name,
                password="StrongPassword123!",
            )
        assert "name" in str(exc.value)


class TestTokenContract:
    def test_token_refresh_request_happy_path(self):
        valid_jwt = f"{'a' * 40}.{'b' * 40}.{'c' * 40}"
        req = TokenRefreshRequest(refresh_token=valid_jwt)
        assert req.refresh_token == valid_jwt

    @pytest.mark.parametrize(
        "invalid_jwt",
        [
            "short.jwt.string",
            f"{'a' * 50}.{'b' * 50}",
            f"{'a' * 40}.{'b' * 40}.{'c' * 30}$$$",
        ],
    )
    def test_token_refresh_request_negative(self, invalid_jwt: str):
        with pytest.raises(ValidationError) as exc:
            TokenRefreshRequest(refresh_token=invalid_jwt)
        assert "refresh_token" in str(exc.value)

    def test_token_payload_type_literal(self):
        payload = TokenPayload(
            sub="123",
            exp=1789146000,
            iat=1789145100,
            type="access",
        )
        assert payload.type == "access"

        with pytest.raises(ValidationError):
            TokenPayload(
                sub="123",
                exp=1789146000,
                iat=1789145100,
                type="custom_type",
            )


class TestComputeAndResponsesContract:
    def test_financial_summary_response_defaults(self):
        summary = FinancialSummaryResponse(
            income=1_000_000,
            expense=400_000,
            total=600_000,
        )
        assert summary.currency == "TOMAN"
        assert summary.total == 600_000

    def test_category_balance_negative_remaining_allowed(self):
        balance = CategoryBalanceResponse(
            name="Travel",
            budget_goal=1_000_000,
            spent=1_500_000,
            remaining=-500_000,
        )
        assert balance.remaining == -500_000
        assert balance.spent == 1_500_000

    def test_category_balance_negative_spent_forbidden(self):
        with pytest.raises(ValidationError) as exc:
            CategoryBalanceResponse(
                name="Travel",
                budget_goal=1_000_000,
                spent=-1,
                remaining=1_000_001,
            )
        assert "spent" in str(exc.value)
