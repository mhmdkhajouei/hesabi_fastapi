import asyncio

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AgeLimit, Retries

from app.config import settings
from app.db.database import async_db_session
from app.db.uow import UnitOfWork
from app.service import ReportJobsService

redis_broker = RedisBroker(url=settings.redis_url)

redis_broker.add_middleware(Retries(max_retries=3))
redis_broker.add_middleware(AgeLimit(max_age=3600 * 1000))

dramatiq.set_broker(redis_broker)


@dramatiq.actor(max_retries=3)
def process_report_actor(job_id: int) -> None:
    async def _run():
        async with async_db_session() as session:
            uow = UnitOfWork(session)
            service = ReportJobsService(uow)
            await service.process_report(job_id)

    asyncio.run(_run())
