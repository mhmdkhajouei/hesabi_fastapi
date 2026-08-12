import asyncio
import httpx

URL = "http://127.0.0.1:8000/api/v1/categories"


async def send_request(client: httpx.AsyncClient, index: int):
    payload = {
        "name": f"Concurrent_Cat_{index}",
        "budget_goal": 1000 + index
    }
    response = await client.post(URL, json=payload)
    return response.status_code, response.json()


async def main():
    async with httpx.AsyncClient() as client:
        # ایجاد ۲۰ درخواست هم‌زمان در Event Loop
        tasks = [send_request(client, i) for i in range(20)]
        results = await asyncio.gather(*tasks)

        # بررسی نتایج
        successes = [res for res in results if res[0] == 200]
        print(f"✅ تعداد درخواست‌های موفق: {len(successes)} از ۲۰")


if __name__ == "__main__":
    asyncio.run(main())