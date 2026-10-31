import json
from decimal import Decimal

from redis.asyncio import Redis


def _default_serializer(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def serialize(data) -> str:
    return json.dumps(data, default=_default_serializer)


def deserialize(raw: str | bytes):
    return json.loads(raw)


def summary_key(household_id: int) -> str:
    return f"compute:summary:{household_id}"


def categories_key(household_id: int) -> str:
    return f"compute:categories:{household_id}"


def category_key(household_id: int, category_id: int) -> str:
    return f"compute:category:{household_id}:{category_id}"


async def invalidate_compute_cache(
    redis: Redis,
    household_id: int,
    category_ids: list[int | None] | None = None,
) -> None:
    keys = [
        summary_key(household_id),
        categories_key(household_id),
    ]

    if category_ids:
        for cid in category_ids:
            if cid is not None:
                keys.append(category_key(household_id, cid))

    await redis.delete(*keys)
