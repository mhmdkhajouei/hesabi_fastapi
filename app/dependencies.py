from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util.typing import Annotated

from app.db.crud import CategoryRepo, ComputeRepo, TransactionRepo
from app.db.database import async_db_session
from app.service import CategoryService, ComputeService, TransactionService
from fastapi import Depends


async def get_session():
    async with async_db_session() as session:
        yield session


def get_category_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CategoryRepo:
    return CategoryRepo(session)


def get_transaction_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TransactionRepo:
    return TransactionRepo(session)


def get_category_service(
    repo: Annotated[CategoryRepo, Depends(get_category_repo)],
) -> CategoryService:
    return CategoryService(repo)


def get_transaction_service(
    repo: Annotated[TransactionRepo, Depends(get_transaction_repo)],
    category_repo: Annotated[CategoryRepo, Depends(get_category_repo)],
) -> TransactionService:
    return TransactionService(repo, category_repo)


def get_compute_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ComputeRepo:
    return ComputeRepo(session)


def get_compute_service(
    repo: Annotated[ComputeRepo, Depends(get_compute_repo)],
) -> ComputeService:
    return ComputeService(repo)
