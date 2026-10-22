import asyncio
import json
import time

import redis.asyncio as redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)


async def slow_function() -> dict:
    await asyncio.sleep(2)
    return {"me": "apple", "jowad": "kiwi"}


async def cache_aside():
    cached = await r.get("fruit_basket")
    if cached:
        return json.loads(cached)

    data = await slow_function()
    await r.set("fruit_basket", json.dumps(data), ex=5)
    return data


async def main():
    await r.ping()
    print("Connected to Redis.")

    print("\n--- First Call (Cache Miss) ---")
    start = time.perf_counter()
    result = await cache_aside()
    end = time.perf_counter()
    print(f"Result: {result}")
    print(f"Time taken: {end - start:.4f} seconds")

    print("\n--- Second Call (Cache Hit) ---")
    start = time.perf_counter()
    result = await cache_aside()
    end = time.perf_counter()
    print(f"Result: {result}")
    print(f"Time taken: {end - start:.4f} seconds")

    print("\n--- Waiting for TTL to expire (6 seconds) ---")
    await asyncio.sleep(6)

    print("\n--- Third Call (After TTL expiration) ---")
    start = time.perf_counter()
    result = await cache_aside()
    end = time.perf_counter()
    print(f"Result: {result}")
    print(f"Time taken: {end - start:.4f} seconds")

    await r.aclose()


if __name__ == "__main__":
    asyncio.run(main())
