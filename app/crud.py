from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, delete
from sqlalchemy.orm import (
    selectinload, joinedload,
)
from app.database import Transaction,Budget,Category,get_session

class BaseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

class CategoryRepo(BaseRepo):

    async def insert_category(self,data: dict) -> Category:
        budget_goal = data.pop("budget_goal", None)
        if budget_goal is None:
            raise HTTPException(status_code=400, detail="category must have budget goal")
        new_category = Category(**data)
        new_category.budget = Budget(goal=budget_goal)
        self.session.add(new_category)
        await self.session.commit()
        return new_category

    async def update_category(self, id: int, data: dict) -> Category | None:
        stmt = select(Category).options(joinedload(Category.budget)).where(Category.id == id)
        category = await self.session.scalar(stmt)

        if not category:
            return None

        if "name" in data:
            category.name = data["name"]
        if "budget_goal" in data:
            category.budget.goal = data["budget_goal"]

        await self.session.commit()
        return category

    async def delete_category(self, id: int):
        stmt = delete(Category).where(Category.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_category(self, id: int) -> Category | None:
        stmt = select(Category).options(joinedload(Category.budget)).where(Category.id == id)
        category = await self.session.scalar(stmt)
        return category

    async def get_all_categories(self):
        stmt = (
            select(Category).
            options(joinedload(Category.budget)).
            order_by(Category.id.asc())
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

    async def update_transaction(self, id: int, data: dict) -> Transaction | None:
        stmt = select(Transaction).options(joinedload(Transaction.category)).where(Transaction.id == id)
        transaction = await self.session.scalar(stmt)
        if transaction is None:
            return None
        for field in ("amount", "type", "note", "category_id"):
            if field in data:
                setattr(transaction, field, data[field])

        await self.session.commit()
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

    async def get_all_transaction(self):
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