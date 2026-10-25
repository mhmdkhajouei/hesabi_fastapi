from unittest.mock import patch

import pytest
from redis.asyncio import Redis
from testcontainers.community.redis import RedisContainer

import app.db.redis as redis_module
from app.config import settings
from app.db.redis import close_redis, get_redis, init_redis


@pytest.fixture(scope="module")
def redis_container():
    with RedisContainer("redis:alpine") as container:
        yield container


@pytest.mark.asyncio
class TestRedisLifespan:
    async def test_init_redis_success(self, redis_container):
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        if "redis_url" in settings.__dict__:
            del settings.__dict__["redis_url"]

        with (
            patch.object(settings, "redis_host", host),
            patch.object(settings, "redis_port", port),
        ):
            client = await init_redis()
            assert client is not None
            assert isinstance(client, Redis)
            assert await client.ping() is True
            await close_redis()
            assert redis_module._redis is None

        if "redis_url" in settings.__dict__:
            del settings.__dict__["redis_url"]

    async def test_get_redis_raises_before_init(self):
        redis_module._redis = None
        with pytest.raises(RuntimeError, match="Redis client is not initialized"):
            get_redis()

    async def test_init_fails_when_redis_unreachable(self):
        if "redis_url" in settings.__dict__:
            del settings.__dict__["redis_url"]

        with (
            patch.object(settings, "redis_host", "localhost"),
            patch.object(settings, "redis_port", 9999),
        ):
            with pytest.raises(Exception):
                await init_redis()
            assert redis_module._redis is None

        if "redis_url" in settings.__dict__:
            del settings.__dict__["redis_url"]

    async def test_close_redis_safe_when_not_initialized(self):
        redis_module._redis = None
        await close_redis()
        assert redis_module._redis is None
