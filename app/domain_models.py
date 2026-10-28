from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from typing import Literal

from app.errors.exceptions import BusinessRuleError


@dataclass
class CategoryDomain:
    name: str
    budget_goal: int
    household_id: int

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:

        if self.household_id is None or self.household_id <= 0:
            raise BusinessRuleError(
                message="Household ID must be a positive integer",
                error_code="INVALID_HOUSEHOLD_ID",
            )

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
    household_id: int
    created_by: int
    type: Literal["income", "expense"]
    date: datetime | None = None
    note: str | None = None
    category_id: int | None = None

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:

        if self.household_id is None or self.household_id <= 0:
            raise BusinessRuleError(
                message="Household ID must be a positive integer",
                error_code="INVALID_HOUSEHOLD_ID",
            )

        if self.created_by is None or self.created_by <= 0:
            raise BusinessRuleError(
                message="Created by user ID must be a positive integer",
                error_code="INVALID_USER_ID",
            )

        if self.amount is None or self.amount <= 0:
            raise BusinessRuleError(
                message="Transaction amount must be strictly greater than zero",
                error_code="INVALID_AMOUNT",
            )
        if self.type == "income" and self.category_id is not None:
            raise BusinessRuleError(
                message="Income transaction cannot reference a category",
                error_code="INCOME_CATEGORY_CONFLICT",
            )
        if self.date:
            if self.date.tzinfo is None:
                self.date = self.date.replace(tzinfo=UTC)

            if self.date > datetime.now(UTC):
                raise BusinessRuleError(
                    message="Transaction date cannot be in the future",
                    error_code="FUTURE_DATE_NOT_ALLOWED",
                )

        if self.note is not None:
            self.note = self.note.strip()
            if len(self.note) > 225:
                raise BusinessRuleError(
                    message="Note cannot exceed 225 characters",
                    error_code="NOTE_TOO_LONG",
                )
            if self.note == "":
                self.note = None


@dataclass
class ReportFiltersDomain:
    start_date: date | None = None
    end_date: date | None = None
    type: Literal["income", "expense"] | None = None
    category_id: int | None = None

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise BusinessRuleError(
                message="Start date cannot be after end date",
                error_code="INVALID_DATE_RANGE",
            )

        if self.category_id is not None and self.category_id <= 0:
            raise BusinessRuleError(
                message="Category ID must be a positive integer",
                error_code="INVALID_CATEGORY_ID",
            )

        if self.type is not None and self.type not in ("income", "expense"):
            raise BusinessRuleError(
                message="Report type must be either 'income' or 'expense'",
                error_code="INVALID_REPORT_TYPE",
            )

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict | None) -> "ReportFiltersDomain | None":
        if not data:
            return None
        return cls(**data)


@dataclass
class ReportJobDomain:
    household_id: int
    requested_by: int
    filters: ReportFiltersDomain | None = None

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        if self.household_id is None or self.household_id <= 0:
            raise BusinessRuleError(
                message="Household ID must be a positive integer",
                error_code="INVALID_HOUSEHOLD_ID",
            )

        if self.requested_by is None or self.requested_by <= 0:
            raise BusinessRuleError(
                message="Requested by user ID must be a positive integer",
                error_code="INVALID_USER_ID",
            )


@dataclass
class RecurringTransactionDomain:
    household_id: int
    created_by: int
    amount: int
    type: Literal["income", "expense"]
    next_run_date: datetime
    is_active: bool = True
    note: str | None = None
    frequency: Literal["daily"] = "daily"
    currency: str = "TOMAN"
    category_id: int | None = None

    def __post_init__(self):
        self.validate()

    def validate(self):
        if self.household_id is None or self.household_id <= 0:
            raise BusinessRuleError(
                message="Household ID must be a positive integer",
                error_code="INVALID_HOUSEHOLD_ID",
            )
        if self.category_id is not None and self.category_id <= 0:
            raise BusinessRuleError(
                message="Category id must be a positive integer",
                error_code="INVALID_CATEGORY_ID",
            )
        if self.created_by is None or self.created_by <= 0:
            raise BusinessRuleError(
                message="Created by user ID must be a positive integer",
                error_code="INVALID_USER_ID",
            )
        if self.amount is None or self.amount <= 0:
            raise BusinessRuleError(
                message="Transaction amount must be strictly greater than zero",
                error_code="INVALID_AMOUNT",
            )
        if self.type == "income" and self.category_id is not None:
            raise BusinessRuleError(
                message="Income transaction cannot reference a category",
                error_code="INCOME_CATEGORY_CONFLICT",
            )
        if self.next_run_date is None:
            raise BusinessRuleError(
                message="Next run date is required",
                error_code="MISSING_NEXT_RUN_DATE",
            )
        if self.next_run_date.tzinfo is None:
            self.next_run_date = self.next_run_date.replace(tzinfo=UTC)
        if self.note is not None:
            self.note = self.note.strip()
            if len(self.note) > 225:
                raise BusinessRuleError(
                    message="Note cannot exceed 225 characters",
                    error_code="NOTE_TOO_LONG",
                )
            if self.note == "":
                self.note = None
