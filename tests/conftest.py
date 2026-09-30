from collections.abc import AsyncIterator, Iterator

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from testcontainers.community.postgres import PostgresContainer

from app.db.database import Base
from app.dependencies import get_session
from app.main import app


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine(
    postgres_container: PostgresContainer,
) -> AsyncIterator[AsyncEngine]:

    async_url = postgres_container.get_connection_url(driver="asyncpg")

    engine = create_async_engine(async_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:

    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
        )

        yield session

        await session.close()
        await transaction.rollback()


@pytest.fixture(autouse=True)
def override_get_session(db_session: AsyncSession) -> Iterator[None]:
    async def _override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = _override_get_session
    try:
        yield
    finally:
        app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncIterator[httpx.AsyncClient]:
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
