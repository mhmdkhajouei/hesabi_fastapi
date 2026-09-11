from datetime import datetime
from typing import Literal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    MetaData,
    String,
    func,
)
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from app.config import settings

CONVERSION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

TransactionType = Enum("expense", "income", name="transaction_type", create_type=True)
CurrencyType = Enum("TOMAN", name="currency_type", create_type=True)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=CONVERSION)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    budget: Mapped["Budget"] = relationship(back_populates="category", uselist=False)
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")

    @property
    def budget_goal(self) -> int:
        return self.budget.goal


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    goal: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(CurrencyType, default="TOMAN", nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    category: Mapped["Category"] = relationship(back_populates="budget")

    __table_args__ = (CheckConstraint("goal > 0", name="check_goal_more_than_zero"),)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[Literal["income", "expense"]] = mapped_column(
        TransactionType, nullable=False
    )
    currency: Mapped[str] = mapped_column(CurrencyType, default="TOMAN", nullable=False)
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    category: Mapped["Category"] = relationship(back_populates="transactions")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_amount_higher_than_zero"),
    )


class Household(Base):
    __tablename__ = "household"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "length(email) >= 5 AND email LIKE '%@%.%'", name="check_user_email_format"
        ),
        CheckConstraint(
            "length(password_hash) > 20", name="check_users_password_hash_length"
        ),
    )


engine = create_async_engine(settings.database_url, echo=True)
async_db_session = async_sessionmaker(engine, expire_on_commit=False)
