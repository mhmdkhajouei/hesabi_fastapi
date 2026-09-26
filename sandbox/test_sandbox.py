import asyncio

import pytest_asyncio

call_tracker = []


@pytest_asyncio.fixture
async def my_resource():
    call_tracker.append("setup")
    await asyncio.sleep(0.01)
    resource = {"is_open": True}

    yield resource

    resource["is_open"] = False
    call_tracker.append("teardown")


async def test_fixture(my_resource) -> None:
    assert my_resource["is_open"] is True
    assert "setup" in call_tracker
