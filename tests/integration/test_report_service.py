import asyncio
import csv
import io
from datetime import UTC, date, datetime
from pathlib import Path
from unittest.mock import patch

import aiofiles
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.db.database import (
    Budget,
    Category,
    Household,
    HouseholdMember,
    HouseholdRole,
    JobStatus,
    ReportJob,
    Transaction,
    User,
)
from app.dependencies import get_report_service, get_uow
from app.errors.exceptions import NotFoundError
from app.schemas import ReportFilters
from app.security import hash_password


@pytest.fixture
def report_service(db_session: AsyncSession):
    uow = get_uow(db_session)
    return get_report_service(uow)


@pytest.fixture
async def report_env(db_session: AsyncSession) -> dict:
    owner = User(
        email="report_owner@hesabi.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Report Owner",
        is_active=True,
    )
    member = User(
        email="report_member@hesabi.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Report Member",
        is_active=True,
    )
    foreign_user = User(
        email="foreign_user@hesabi.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Foreign User",
        is_active=True,
    )
    db_session.add_all([owner, member, foreign_user])
    await db_session.flush()

    household = Household(name="Primary Household", is_personal=False)
    foreign_household = Household(name="Foreign Household", is_personal=False)
    db_session.add_all([household, foreign_household])
    await db_session.flush()

    memberships = [
        HouseholdMember(
            user_id=owner.id,
            household_id=household.id,
            role=HouseholdRole.OWNER,
        ),
        HouseholdMember(
            user_id=member.id,
            household_id=household.id,
            role=HouseholdRole.MEMBER,
        ),
        HouseholdMember(
            user_id=foreign_user.id,
            household_id=foreign_household.id,
            role=HouseholdRole.OWNER,
        ),
    ]
    db_session.add_all(memberships)

    category = Category(
        name="Food",
        household_id=household.id,
        budget=Budget(goal=2_000_000),
    )
    foreign_category = Category(
        name="Foreign Cat",
        household_id=foreign_household.id,
        budget=Budget(goal=1_000_000),
    )
    db_session.add_all([category, foreign_category])
    await db_session.flush()

    tx1 = Transaction(
        amount=150_000,
        type="expense",
        household_id=household.id,
        created_by=owner.id,
        category_id=category.id,
        date=datetime(2026, 5, 10, 12, 0, tzinfo=UTC),
        note="Groceries Shopping",
    )
    tx2 = Transaction(
        amount=500_000,
        type="income",
        household_id=household.id,
        created_by=member.id,
        category_id=None,
        date=datetime(2026, 6, 15, 9, 30, tzinfo=UTC),
        note="Freelance Project",
    )
    tx_foreign = Transaction(
        amount=300_000,
        type="expense",
        household_id=foreign_household.id,
        created_by=foreign_user.id,
        category_id=foreign_category.id,
        date=datetime(2026, 5, 12, 10, 0, tzinfo=UTC),
        note="Foreign Note",
    )
    db_session.add_all([tx1, tx2, tx_foreign])
    await db_session.commit()

    return {
        "owner": owner,
        "member": member,
        "foreign_user": foreign_user,
        "household": household,
        "foreign_household": foreign_household,
        "category": category,
        "foreign_category": foreign_category,
        "tx1": tx1,
        "tx2": tx2,
    }


class TestReportJobsService:
    async def test_create_job_happy_path(self, report_service, report_env):
        filters = ReportFilters(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            type="expense",
            category_id=report_env["category"].id,
        )

        response = await report_service.create_job(
            household_id=report_env["household"].id,
            user_id=report_env["owner"].id,
            filters=filters,
        )

        assert response.id is not None
        assert response.status == JobStatus.PENDING
        assert response.file_path is None
        assert response.error_message is None
        assert response.filters["start_date"] == "2026-01-01"
        assert response.filters["end_date"] == "2026-12-31"
        assert response.filters["type"] == "expense"
        assert response.filters["category_id"] == report_env["category"].id

    async def test_create_job_empty_filters(self, report_service, report_env):
        response = await report_service.create_job(
            household_id=report_env["household"].id,
            user_id=report_env["owner"].id,
            filters=None,
        )

        assert response.id is not None
        assert response.status == JobStatus.PENDING
        assert response.filters is None
        assert response.file_path is None

    async def test_create_report_single_boundary_filters(
        self, report_service, report_env
    ):
        filters = ReportFilters(start_date=date(2026, 5, 1))

        response = await report_service.create_job(
            household_id=report_env["household"].id,
            user_id=report_env["owner"].id,
            filters=filters,
        )

        assert response.id is not None
        assert response.filters == {"start_date": "2026-05-01"}

    async def test_create_job_concurrent_requests(self, test_engine: AsyncEngine):
        session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

        async with session_factory() as session:
            user = User(
                email="concurrent_report@hesabi.com",
                password_hash=hash_password("StrongPassword123!"),
                name="Concurrent User",
                is_active=True,
            )
            household = Household(name="Concurrent HH", is_personal=False)
            session.add_all([user, household])
            await session.flush()

            session.add(
                HouseholdMember(
                    user_id=user.id,
                    household_id=household.id,
                    role=HouseholdRole.OWNER,
                )
            )
            await session.commit()
            user_id = user.id
            household_id = household.id

        async def _create_single_job():
            async with session_factory() as session:
                uow = get_uow(session)
                service = get_report_service(uow)
                return await service.create_job(
                    household_id=household_id,
                    user_id=user_id,
                    filters=None,
                )

        tasks = [_create_single_job() for _ in range(5)]
        responses = await asyncio.gather(*tasks)

        assert len(responses) == 5
        job_ids = {r.id for r in responses}
        assert len(job_ids) == 5
        for r in responses:
            assert r.status == JobStatus.PENDING

    async def test_create_report_with_foreign_category_id(
        self, report_service, report_env
    ):
        filters = ReportFilters(category_id=report_env["foreign_category"].id)

        job = await report_service.create_job(
            household_id=report_env["household"].id,
            user_id=report_env["owner"].id,
            filters=filters,
        )

        await report_service.process_report(job.id)
        status_res = await report_service.get_job_status(
            report_env["household"].id, job.id, report_env["owner"].id
        )

        assert status_res.status == JobStatus.COMPLETED
        file_path = Path(status_res.file_path)
        try:
            async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
                content = await f.read()
                reader = list(csv.reader(io.StringIO(content)))
                assert len(reader) == 1
                assert reader[0] == [
                    "ID",
                    "Amount",
                    "Type",
                    "Category",
                    "Creator",
                    "Date",
                    "Note",
                ]
        finally:
            file_path.unlink(missing_ok=True)

    async def test_get_job_status_happy_path(self, report_service, report_env):
        job = await report_service.create_job(
            household_id=report_env["household"].id,
            user_id=report_env["owner"].id,
            filters=None,
        )

        status_res = await report_service.get_job_status(
            household_id=report_env["household"].id,
            job_id=job.id,
            user_id=report_env["owner"].id,
        )

        assert status_res.id == job.id
        assert status_res.status == JobStatus.PENDING

    async def test_get_job_status_not_found(self, report_service, report_env):
        with pytest.raises(NotFoundError) as exc_info:
            await report_service.get_job_status(
                household_id=report_env["household"].id,
                job_id=999_999,
                user_id=report_env["owner"].id,
            )

        assert exc_info.value.error_code == "REPORT_NOT_FOUND"

    async def test_get_job_status_cross_user_forbidden(
        self, report_service, report_env
    ):
        job = await report_service.create_job(
            household_id=report_env["household"].id,
            user_id=report_env["owner"].id,
            filters=None,
        )

        with pytest.raises(NotFoundError) as exc_info:
            await report_service.get_job_status(
                household_id=report_env["household"].id,
                job_id=job.id,
                user_id=report_env["member"].id,
            )

        assert exc_info.value.error_code == "REPORT_NOT_FOUND"

    async def test_get_report_cross_household_bola(self, report_service, report_env):
        job = await report_service.create_job(
            household_id=report_env["household"].id,
            user_id=report_env["owner"].id,
            filters=None,
        )

        with pytest.raises(NotFoundError) as exc_info:
            await report_service.get_job_status(
                household_id=report_env["foreign_household"].id,
                job_id=job.id,
                user_id=report_env["owner"].id,
            )

        assert exc_info.value.error_code == "REPORT_NOT_FOUND"

    async def test_process_report_happy_path(self, report_service, report_env):
        job = await report_service.create_job(
            household_id=report_env["household"].id,
            user_id=report_env["owner"].id,
            filters=None,
        )

        await report_service.process_report(job.id)

        status_res = await report_service.get_job_status(
            household_id=report_env["household"].id,
            job_id=job.id,
            user_id=report_env["owner"].id,
        )

        assert status_res.status == JobStatus.COMPLETED
        assert status_res.file_path is not None
        assert status_res.completed_at is not None

        file_path = Path(status_res.file_path)
        assert file_path.exists()
        try:
            async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
                content = await f.read()
                rows = list(csv.reader(io.StringIO(content)))
                assert len(rows) == 3
                assert rows[0] == [
                    "ID",
                    "Amount",
                    "Type",
                    "Category",
                    "Creator",
                    "Date",
                    "Note",
                ]
                data_rows = rows[1:]
                amounts = [r[1] for r in data_rows]
                assert "150000" in amounts
                assert "500000" in amounts
        finally:
            file_path.unlink(missing_ok=True)

    async def test_process_report_empty_result(
        self, report_service, report_env, db_session
    ):
        empty_hh = Household(name="Empty Household", is_personal=False)
        db_session.add(empty_hh)
        await db_session.flush()

        db_session.add(
            HouseholdMember(
                user_id=report_env["owner"].id,
                household_id=empty_hh.id,
                role=HouseholdRole.OWNER,
            )
        )
        await db_session.commit()

        job = await report_service.create_job(
            household_id=empty_hh.id,
            user_id=report_env["owner"].id,
            filters=None,
        )

        await report_service.process_report(job.id)

        status_res = await report_service.get_job_status(
            empty_hh.id, job.id, report_env["owner"].id
        )

        assert status_res.status == JobStatus.COMPLETED
        file_path = Path(status_res.file_path)
        try:
            async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
                content = await f.read()
                rows = list(csv.reader(io.StringIO(content)))
                assert len(rows) == 1
                assert rows[0] == [
                    "ID",
                    "Amount",
                    "Type",
                    "Category",
                    "Creator",
                    "Date",
                    "Note",
                ]
        finally:
            file_path.unlink(missing_ok=True)

    async def test_process_report_exception_handling(
        self, report_service, report_env, db_session
    ):
        job = await report_service.create_job(
            household_id=report_env["household"].id,
            user_id=report_env["owner"].id,
            filters=None,
        )

        with (
            patch("aiofiles.open", side_effect=OSError("Disk write error")),
            pytest.raises(OSError),
        ):
            await report_service.process_report(job.id)

        query = select(ReportJob).where(ReportJob.id == job.id)
        result = await db_session.execute(query)
        db_job = result.scalar_one()

        assert db_job.status == JobStatus.FAILED
        assert "Disk write error" in db_job.error_message
        assert db_job.completed_at is not None

    async def test_process_report_with_special_characters_and_persian_text(
        self, report_service, report_env, db_session
    ):
        persian_cat = Category(
            name="خواربار",
            household_id=report_env["household"].id,
            budget=Budget(goal=3_000_000),
        )
        db_session.add(persian_cat)
        await db_session.flush()

        tx = Transaction(
            amount=750_000,
            type="expense",
            household_id=report_env["household"].id,
            created_by=report_env["owner"].id,
            category_id=persian_cat.id,
            date=datetime(2026, 7, 1, 14, 0, tzinfo=UTC),
            note="خرید سوپرمارکت، گوشت و مرغ\nقسط ۱",
        )
        db_session.add(tx)
        await db_session.commit()

        job = await report_service.create_job(
            household_id=report_env["household"].id,
            user_id=report_env["owner"].id,
            filters=ReportFilters(category_id=persian_cat.id),
        )

        await report_service.process_report(job.id)

        status_res = await report_service.get_job_status(
            report_env["household"].id, job.id, report_env["owner"].id
        )

        assert status_res.status == JobStatus.COMPLETED
        file_path = Path(status_res.file_path)
        try:
            async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
                content = await f.read()
                rows = list(csv.reader(io.StringIO(content)))
                assert len(rows) == 2
                assert rows[1][3] == "خواربار"
                assert rows[1][6] == "خرید سوپرمارکت، گوشت و مرغ\nقسط ۱"
        finally:
            file_path.unlink(missing_ok=True)

    async def test_process_report_transactions_with_null_category_and_creator(
        self, report_service, report_env
    ):
        job = await report_service.create_job(
            household_id=report_env["household"].id,
            user_id=report_env["owner"].id,
            filters=ReportFilters(type="income"),
        )

        await report_service.process_report(job.id)

        status_res = await report_service.get_job_status(
            report_env["household"].id, job.id, report_env["owner"].id
        )

        file_path = Path(status_res.file_path)
        try:
            async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
                content = await f.read()
                rows = list(csv.reader(io.StringIO(content)))
                assert len(rows) == 2
                assert rows[1][3] == "N/A"
                assert rows[1][2] == "income"
        finally:
            file_path.unlink(missing_ok=True)

    async def test_process_report_missing_job_early_return(self, report_service):
        result = await report_service.process_report(999_999)
        assert result is None

    async def test_process_report_creates_directory_if_not_exists(
        self, report_service, report_env
    ):
        job = await report_service.create_job(
            household_id=report_env["household"].id,
            user_id=report_env["owner"].id,
            filters=None,
        )

        reports_dir = Path("data/reports")
        await report_service.process_report(job.id)

        status_res = await report_service.get_job_status(
            report_env["household"].id, job.id, report_env["owner"].id
        )

        assert reports_dir.exists()
        assert reports_dir.is_dir()

        file_path = Path(status_res.file_path)
        assert file_path.exists()
        file_path.unlink(missing_ok=True)
