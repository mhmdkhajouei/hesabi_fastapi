from sqlalchemy import and_, delete, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    joinedload,
    selectinload,
)

from app.db.models import Budget, Category, Transaction


class BaseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session


class CategoryRepo(BaseRepo):
    async def insert_category(self, data: dict) -> Category:
        data_copy = data.copy()
        budget_goal = data_copy.pop("budget_goal", None)
        new_category = Category(**data_copy)
        new_category.budget = Budget(goal=budget_goal)
        self.session.add(new_category)
        await self.session.commit()
        await self.session.refresh(new_category, ["budget"])
        return new_category

    async def update_category(self, category: Category, data: dict) -> Category | None:
        if "name" in data:
            category.name = data["name"]
        if "budget_goal" in data:
            category.budget.goal = data["budget_goal"]

        await self.session.commit()
        await self.session.refresh(category, ["budget"])
        return category

    async def delete_category(self, id: int):
        stmt = delete(Category).where(Category.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_category(self, id: int) -> Category | None:
        stmt = (
            select(Category)
            .options(joinedload(Category.budget))
            .where(Category.id == id)
        )
        category = await self.session.scalar(stmt)
        return category

    async def get_all_categories(self):
        stmt = (
            select(Category)
            .options(joinedload(Category.budget))
            .order_by(Category.id.asc())
        )
        result = (await self.session.scalars(stmt)).unique().all()
        return result

    async def check_category(self, id: int) -> bool:
        stmt = select(exists().where(Category.id == id))
        result = await self.session.scalar(stmt)
        return bool(result)


class BudgetRepo(BaseRepo):
    pass


class TransactionRepo(BaseRepo):
    async def insert_transaction(self, data: dict) -> Transaction:
        new_transaction = Transaction(**data)
        self.session.add(new_transaction)
        await self.session.commit()
        await self.session.refresh(new_transaction)
        return new_transaction

    async def update_transaction(
        self, transaction: Transaction, data: dict
    ) -> Transaction | None:

        for field in ("amount", "type", "note", "category_id", "date"):
            if field in data:
                setattr(transaction, field, data[field])

        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def delete_transaction(self, id: int) -> bool:
        stmt = delete(Transaction).where(Transaction.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_transaction(self, id: int) -> Transaction | None:
        stmt = (
            select(Transaction)
            .options(joinedload(Transaction.category))
            .where(Transaction.id == id)
        )
        transaction = await self.session.scalar(stmt)
        return transaction

    async def get_all_transactions(self):
        stmt = (
            select(Transaction)
            .options(selectinload(Transaction.category))
            .order_by(Transaction.id.asc())
        )
        result = (await self.session.scalars(stmt)).all()
        return result

    async def check_transaction(self, id: int) -> bool:
        stmt = select(exists().where(Transaction.id == id))
        result = await self.session.scalar(stmt)
        return bool(result)


class ComputeRepo(BaseRepo):
    async def get_total_amount_by_type(self, transaction_type: str) -> int:
        stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.type == transaction_type
        )

        result = await self.session.scalar(stmt)
        return int(result or 0)

    async def get_category_balance(self, category_id: int):
        stmt = (
            select(
                Category.name.label("category_name"),
                Budget.goal.label("budget_goal"),
                func.coalesce(func.sum(Transaction.amount), 0).label("spent"),
            )
            .join(Budget, Category.id == Budget.category_id)
            .outerjoin(
                Transaction,
                and_(
                    Category.id == Transaction.category_id,
                    Transaction.type == "expense",
                ),
            )
            .where(Category.id == category_id)
            .group_by(Category.id, Category.name, Budget.goal)
        )

        result = await self.session.execute(stmt)
        return result.mappings().first()

    async def get_all_categories_balance(self):
        stmt = (
            select(
                Category.name.label("category_name"),
                Budget.goal.label("budget_goal"),
                func.coalesce(func.sum(Transaction.amount), 0).label("spent"),
            )
            .join(Budget, Category.id == Budget.category_id)
            .outerjoin(
                Transaction,
                and_(
                    Category.id == Transaction.category_id,
                    Transaction.type == "expense",
                ),
            )
            .group_by(Category.id, Category.name, Budget.goal)
            .order_by(Category.id.asc())
        )

        result = await self.session.execute(stmt)
        return result.mappings().all()
