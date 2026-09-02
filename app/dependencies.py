from datetime import UTC, datetime
from email.utils import format_datetime

from fastapi import Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util.typing import Annotated

from app.db.crud import CategoryRepo, ComputeRepo, TransactionRepo
from app.db.database import async_db_session
from app.service import CategoryService, ComputeService, TransactionService


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


class DeprecateRoute:
    def __init__(
        self,
        sunset_date: datetime | str | None = None,
        alternative_url: str | None = None,
    ):
        self.sunset_date = self._format_sunset(sunset_date)
        self.alternative_url = alternative_url

    @staticmethod
    def _format_sunset(sunset: datetime | str | None) -> str | None:
        if isinstance(sunset, datetime):
            if sunset.tzinfo is None:
                sunset = sunset.replace(tzinfo=UTC)
            return format_datetime(sunset, usegmt=True)
        return sunset

    async def __call__(self, response: Response) -> None:
        response.headers["Deprecation"] = "true"

        if self.sunset_date:
            response.headers["Sunset"] = self.sunset_date

        if self.alternative_url:
            response.headers["Link"] = (
                f'<{self.alternative_url}>; rel="successor-version"'
            )
