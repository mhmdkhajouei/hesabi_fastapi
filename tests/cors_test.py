import asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app


async def run_pipeline_tests():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        print("--- ۱. تست تولید خودکار X-Request-Id و هدرهای امنیتی پایه ---")
        res_sec = await client.get("/docs")
        print("Status:", res_sec.status_code)
        print("X-Request-Id (Auto Generated):", res_sec.headers.get("x-request-id"))
        print(
            "X-Content-Type-Options:",
            res_sec.headers.get("x-content-type-options"),
        )
        print("X-Frame-Options:", res_sec.headers.get("x-frame-options"))

        print("\n--- ۲. تست حفظ X-Request-Id ارسالی از سمت کلاینت ---")
        custom_req_id = "custom-client-trace-id-12345"
        res_custom = await client.get(
            "/docs", headers={"X-Request-Id": custom_req_id}
        )
        print("Status:", res_custom.status_code)
        print("X-Request-Id (Preserved):", res_custom.headers.get("x-request-id"))

        print("\n--- ۳. تست Origin مجاز (CORS GET) ---")
        headers_allowed = {"Origin": "http://localhost:3000"}
        res_ok = await client.get("/docs", headers=headers_allowed)
        print("Status:", res_ok.status_code)
        print(
            "Access-Control-Allow-Origin:",
            res_ok.headers.get("access-control-allow-origin"),
        )
        print("X-Request-Id:", res_ok.headers.get("x-request-id"))

        print("\n--- ۴. تست Preflight (CORS OPTIONS) ---")
        headers_preflight = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization,Content-Type",
        }
        res_opt = await client.options("/docs", headers=headers_preflight)
        print("Status:", res_opt.status_code)
        print(
            "Access-Control-Allow-Origin:",
            res_opt.headers.get("access-control-allow-origin"),
        )
        print(
            "Access-Control-Allow-Methods:",
            res_opt.headers.get("access-control-allow-methods"),
        )

        print("\n--- ۵. تست Origin غیرمجاز (Disallowed) ---")
        headers_disallowed = {"Origin": "https://evil.example"}
        res_evil = await client.get("/docs", headers=headers_disallowed)
        print("Status:", res_evil.status_code)
        print(
            "Access-Control-Allow-Origin:",
            res_evil.headers.get("access-control-allow-origin"),
        )
        print("X-Request-Id:", res_evil.headers.get("x-request-id"))


if __name__ == "__main__":
    asyncio.run(run_pipeline_tests())