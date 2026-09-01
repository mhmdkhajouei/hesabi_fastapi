from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import CategoryRepo, TransactionRepo
from app.db.database import async_db_session
from app.service import CategoryService, TransactionService


async def get_session():
    async with async_db_session() as session:
        yield session


def get_category_repo(
    session: AsyncSession = Depends(get_session),
) -> CategoryRepo:
    return CategoryRepo(session)


def get_transaction_repo(
    session: AsyncSession = Depends(get_session),
) -> TransactionRepo:
    return TransactionRepo(session)


def get_category_service(
    repo: CategoryRepo = Depends(get_category_repo),
) -> CategoryService:
    return CategoryService(repo)


def get_transaction_service(
    repo: TransactionRepo = Depends(get_transaction_repo),
    category_repo: CategoryRepo = Depends(get_category_repo),
) -> TransactionService:
    return TransactionService(repo, category_repo)
