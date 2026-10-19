import asyncio

from sqlalchemy import CheckConstraint, select, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from testcontainers.community.postgres import PostgresContainer


class Base(DeclarativeBase):
    pass


class Counter(Base):
    __tablename__ = "counter"

    id: Mapped[int] = mapped_column(primary_key=True)
    val: Mapped[int] = mapped_column(nullable=False)


class SandboxRecord(Base):
    __tablename__ = "sandboxrecord"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_sandbox_amount_positive"),
        CheckConstraint("category_id > 0", name="check_sandbox_category_positive"),
    )


async def init_db(
    container: PostgresContainer,
) -> tuple[AsyncEngine, async_sessionmaker]:
    database_url = container.get_connection_url(driver="asyncpg")
    engine = create_async_engine(database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return engine, session_factory


async def _read_unsafe(session_factory: async_sessionmaker):
    async with session_factory() as session:
        stmt = select(Counter).where(Counter.id == 1)
        counter = await session.scalar(stmt)
        await asyncio.sleep(0.01)
        counter.val += 1
        await session.commit()


async def _read_safe(session_factory: async_sessionmaker):
    async with session_factory() as session:
        stmt = select(Counter).where(Counter.id == 1).with_for_update()
        counter = await session.scalar(stmt)
        await asyncio.sleep(0.01)
        counter.val += 1
        await session.commit()


async def test_lost_update_race(session_factory: async_sessionmaker):
    async with session_factory() as session:
        session.add(Counter(id=1, val=0))
        await session.commit()

        print("shooting 50 task concurrency")

        tasks = [_read_unsafe(session_factory) for _ in range(50)]
        await asyncio.gather(*tasks)

        async with session_factory() as session:
            stmt = select(Counter).where(Counter.id == 1)
            result = await session.scalar(stmt)
            print(f"final result: {result.val}")


async def test_pessimistic_locking(session_factory: async_sessionmaker):
    async with session_factory() as session:
        session.add(Counter(id=1, val=0))
        await session.commit()

        print("shooting 50 task concurrency")

        tasks = [_read_safe(session_factory) for _ in range(50)]
        await asyncio.gather(*tasks)

        async with session_factory() as session:
            stmt = select(Counter).where(Counter.id == 1)
            result = await session.scalar(stmt)
            print(f"final result: {result.val}")


async def test_index_profiling(
    engine: AsyncEngine, session_factory: async_sessionmaker
):
    query = text("""
            EXPLAIN (ANALYZE, BUFFERS)
            SELECT category_id, amount
            FROM sandboxrecord
            WHERE category_id = 5;
        """)
    async with session_factory() as session:
        insert_sql = text("""
                INSERT INTO sandboxrecord (category_id, amount)
                SELECT
                    (floor(random() * 50) + 1)::int,
                    (floor(random() * 100000) +1)::int
                FROM generate_series(1, 100000);
        """)
        await session.execute(insert_sql)
        await session.commit()

        result_before = await session.execute(query)
        for row in result_before.fetchall():
            print(row[0])
    print("----------------------------------")
    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(
            text(
                """
                    CREATE INDEX idx_sandbox_category_covering
                    ON sandboxrecord (category_id)
                    INCLUDE (amount);
        """
            )
        )
        await conn.execute(text("VACUUM ANALYZE sandboxrecord"))

    async with session_factory() as session:
        result_after = await session.execute(query)
        for row in result_after.fetchall():
            print(row[0])


async def main():
    with PostgresContainer("postgres:16-alpine") as container:
        engine, session_factory = await init_db(container)

        # await test_lost_update_race(session_factory)
        # await test_pessimistic_locking(session_factory)
        await test_index_profiling(engine, session_factory)

        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
