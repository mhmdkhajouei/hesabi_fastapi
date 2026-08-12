import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import ForeignKey, Enum, DateTime, func
from sqlalchemy import CheckConstraint,String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

load_dotenv()
DATABASE_URL= os.environ["DATABASE_URL"]

TransactionType = Enum("expense", "income", name= "transaction_type", create_type=True)
CurrencyType = Enum("TOMAN", name="currency_type", create_type=True)

class Base(DeclarativeBase):
    pass

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    budget: Mapped["Budget"] = relationship(back_populates="category", uselist=False)
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    goal: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(CurrencyType, default="TOMAN", nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, unique=True)

    category: Mapped["Category"] = relationship(back_populates="budget")

    __table_args__ = (
        CheckConstraint("goal > 0", name="check_goal_more_than_zero"),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(TransactionType, nullable=False)
    currency: Mapped[str] = mapped_column(CurrencyType, default="TOMAN", nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    note: Mapped[str | None] = mapped_column(String(225),nullable=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    category: Mapped["Category"] = relationship(back_populates="transactions")

    __table_args__ = (

        CheckConstraint("amount > 0", name="check_amount_higher_than_zero"),
    )


engine = create_async_engine(DATABASE_URL, echo=True)
async_db_session = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session():
    async with async_db_session() as session:
        yield session

