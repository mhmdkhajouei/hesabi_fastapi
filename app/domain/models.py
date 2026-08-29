from dataclasses import dataclass
from datetime import UTC, datetime

from app.errors.exceptions import BusinessRuleError


@dataclass
class CategoryDomain:
    name: str
    budget_goal: int

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:

        if self.name is None or not self.name.strip():
            raise BusinessRuleError(
                message="Category name can not be empty",
                error_code="INVALID_CATEGORY_NAME",
            )

        self.name = self.name.strip()

        if len(self.name) > 20:
            raise BusinessRuleError(
                message="Category name cannot exceed 20 characters",
                error_code="CATEGORY_NAME_TOO_LONG",
            )

        if self.budget_goal is None or self.budget_goal <= 0:
            raise BusinessRuleError(
                message="Budget goal must be strictly greater than zero",
                error_code="INVALID_BUDGET_GOAL",
            )


@dataclass
class TransactionDomain:
    amount: int
    type: str
    date: datetime | None = None
    note: str | None = None
    category_id: int | None = None

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:

        if self.amount is None or self.amount <= 0:
            raise BusinessRuleError(
                message="Transaction amount must be strictly greater than zero",
                error_code="INVALID_AMOUNT",
            )
        if self.type not in ["income", "expense"]:
            raise BusinessRuleError(
                message="Transaction type must be either income or expense",
                error_code="INVALID_TRANSACTION_TYPE",
            )
        if self.type == "income" and self.category_id is not None:
            raise BusinessRuleError(
                message="Income transaction cannot reference a category",
                error_code="INCOME_CATEGORY_CONFLICT",
            )
        if self.date:
            target_date = self.date
            if target_date.tzinfo is None:
                target_date = target_date.replace(tzinfo=UTC)

            if target_date > datetime.now(UTC):
                raise BusinessRuleError(
                    message="Transaction date cannot be in the future",
                    error_code="FUTURE_DATE_NOT_ALLOWED",
                )

        if self.note:
            self.note = self.note.strip()
            if len(self.note) > 225:
                raise BusinessRuleError(
                    message="Note cannot exceed 225 characters",
                    error_code="NOTE_TOO_LONG",
                )
            if self.note == "":
                self.note = None
