import asyncio

import dramatiq

from app.broker import redis_broker  # noqa: F401
from app.db.database import async_db_session
from app.db.uow import UnitOfWork
from app.service import RecurringTransactionService, ReportJobsService


@dramatiq.actor(max_retries=3)
def process_report_actor(job_id: int) -> None:
    async def _run():
        async with async_db_session() as session:
            uow = UnitOfWork(session)
            service = ReportJobsService(uow)
            await service.process_report(job_id)

    asyncio.run(_run())


@dramatiq.actor(max_retries=3)
def process_recurring_template_actor(template_id: int) -> None:
    async def _run():
        async with async_db_session() as session:
            uow = UnitOfWork(session)
            service = RecurringTransactionService(uow)

            await service.process_single_template(template_id)

    asyncio.run(_run())
