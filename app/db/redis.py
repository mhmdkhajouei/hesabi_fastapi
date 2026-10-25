from redis.asyncio import Redis

from app.config import settings

_redis: Redis | None = None


async def init_redis() -> Redis:
    global _redis
    client = Redis.from_url(
        settings.redis_url, decode_responses=True, health_check_interval=30
    )
    await client.ping()
    _redis = client
    return client


async def close_redis() -> None:
    global _redis
    if _redis is None:
        return
    await _redis.aclose()
    _redis = None


def get_redis() -> Redis:
    if _redis is None:
        raise RuntimeError(
            "Redis client is not initialized"
            "Ensure init_redis() is called in the FastAPI lifespan"
        )

    return _redis
