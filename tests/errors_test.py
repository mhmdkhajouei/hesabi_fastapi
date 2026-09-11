# test_errors_quick.py
import asyncio

from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel, Field

from app.errors.exceptions import NotFoundError
from app.main import app  # همان اپ که هندلرها به آن متصل شده‌اند


# ۱. تعریف دو مسیر آزمایشی برای شبیه‌سازی خطاها
class DummyPayload(BaseModel):
    amount: int = Field(gt=0)


@app.post("/test/dummy")
async def dummy_endpoint(payload: DummyPayload):
    return {"success": True}


@app.get("/test/trigger-not-found")
async def trigger_not_found():
    raise NotFoundError(message="Item does not exist", error_code="ITEM_NOT_FOUND")


# ۲. اجرای تست‌ها
async def run_tests():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        print("--- ۱. تست اعتبارسنجی پایدانتیک (۴۲۲) ---")
        res_val = await client.post("/test/dummy", json={"amount": -10})
        print("Status:", res_val.status_code)
        print("Body:", res_val.json())

        print("\n--- ۲. تست خطای اختصاصی NotFoundError (۴۰۴) ---")
        res_nf = await client.get("/test/trigger-not-found")
        print("Status:", res_nf.status_code)
        print("Body:", res_nf.json())

        print("\n--- ۳. تست خطای روتینگ Starlette (مسیر نامعتبر) ---")
        res_starlette = await client.get("/non-existing-route")
        print("Status:", res_starlette.status_code)
        print("Body:", res_starlette.json())


if __name__ == "__main__":
    asyncio.run(run_tests())
