from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import BudgetRepo, CategoryRepo, ComputeRepo, TransactionRepo


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        self.transactions = TransactionRepo(self.session)
        self.categories = CategoryRepo(self.session)
        self.budgets = BudgetRepo(self.session)
        self.compute = ComputeRepo(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()
