import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AgeLimit, Callbacks, Pipelines, Retries, TimeLimit

from app.config import settings

redis_broker = RedisBroker(
    url=settings.redis_url,
    middleware=[
        AgeLimit(max_age=3600 * 1000),
        TimeLimit(),
        Callbacks(),
        Pipelines(),
        Retries(max_retries=3),
    ],
)
dramatiq.set_broker(redis_broker)


def enqueue_recurring_transaction(template_id: int, delay_seconds: float):
    from app.worker import process_recurring_template_actor

    process_recurring_template_actor.send_with_options(
        args=(template_id,), delay=int(delay_seconds * 1000)
    )
