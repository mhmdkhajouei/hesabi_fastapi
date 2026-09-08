from datetime import UTC, datetime
from email.utils import format_datetime

from fastapi import Depends, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util.typing import Annotated

from app.db.crud import CategoryRepo, ComputeRepo, TransactionRepo, UserRepo
from app.db.database import User, async_db_session
from app.errors.exceptions import AuthenticationError
from app.security import decode_token
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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_user_repo(session: Annotated[AsyncSession, Depends(get_session)]) -> UserRepo:
    return UserRepo(session)


async def get_current_user(
    repo: Annotated[UserRepo, Depends(get_user_repo)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:

    payload = decode_token(token)

    if payload.type != "access":
        raise AuthenticationError(
            message="Invalid token type for authentication",
            error_code="INVALID_TOKEN_TYPE",
        )

    if not payload.sub.isdigit():
        raise AuthenticationError(
            message="Invalid token subject",
            error_code="INVALID_TOKEN_SUBJECT",
        )

    user = await repo.get_user_by_id(int(payload.sub))

    if not user:
        raise AuthenticationError(
            message="User not found",
            error_code="USER_NOT_FOUND",
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise AuthenticationError(
            message="User account is deactivated",
            error_code="USER_DEACTIVATED",
        )

    return current_user
