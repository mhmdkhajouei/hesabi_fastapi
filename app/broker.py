import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AgeLimit, Retries

from app.config import settings

redis_broker = RedisBroker(url=settings.redis_url)
redis_broker.add_middleware(Retries(max_retries=3))
redis_broker.add_middleware(AgeLimit(max_age=3600 * 1000))

dramatiq.set_broker(redis_broker)
