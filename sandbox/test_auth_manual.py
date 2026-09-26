import asyncio
import time

from httpx import ASGITransport, AsyncClient

from app.main import app

BASE_URL = "http://testserver/api/v1/auth"


async def run_auth_tests():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # ساخت ایمیل یکتا برای جلوگیری از شکست تست اول در اجراهای مکرر
        unique_suffix = int(time.time())
        test_email = f"tester_{unique_suffix}@hesabi.dev"
        test_pass = "StrongP@ssw0rd123!"

        print("--- ۱. تست ثبت‌نام کاربر جدید (POST /auth/register) ---")
        reg_payload = {
            "email": test_email,
            "password": test_pass,
            "name": "Hesabi Tester",
        }
        res_reg = await client.post(f"{BASE_URL}/register", json=reg_payload)
        print("Status:", res_reg.status_code)
        print("Body:", res_reg.json())
        assert res_reg.status_code in [200, 201], f"Registration failed: {res_reg.text}"

        print("\n--- ۲. تست ثبت‌نام با ایمیل تکراری (Duplicate Conflict) ---")
        res_dup = await client.post(f"{BASE_URL}/register", json=reg_payload)
        print("Status:", res_dup.status_code)
        print("Body:", res_dup.json())
        assert res_dup.status_code in [400, 409, 422], (
            f"Unexpected status: {res_dup.status_code}"
        )

        print("\n--- ۳. تست ورود ناموفق (رمز عبور اشتباه) ---")
        res_wrong_login = await client.post(
            f"{BASE_URL}/login",
            json={"email": test_email, "password": "WrongPassword123!"},
        )
        print("Status:", res_wrong_login.status_code)
        print("Body:", res_wrong_login.json())
        assert res_wrong_login.status_code == 401

        print("\n--- ۴. تست ورود موفق و دریافت جفت‌توکن JWT (POST /auth/login) ---")
        res_login = await client.post(
            f"{BASE_URL}/login",
            json={"email": test_email, "password": test_pass},
        )
        print("Status:", res_login.status_code)
        tokens = res_login.json()
        print("Tokens received:", list(tokens.keys()))
        assert res_login.status_code == 200
        assert "access_token" in tokens and "refresh_token" in tokens

        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        print(
            "\n--- ۵. تست Refresh Token و تمدید Access Token (POST /auth/refresh) ---"
        )
        res_refresh = await client.post(
            f"{BASE_URL}/refresh",
            json={"refresh_token": refresh_token},
        )
        print("Status:", res_refresh.status_code)
        print("Body:", res_refresh.json())
        assert res_refresh.status_code == 200
        assert "access_token" in res_refresh.json()

        print(
            "\n--- ۶. تست ارسال Access Token به جای Refresh Token (Type Mismatch) ---"
        )
        res_bad_refresh = await client.post(
            f"{BASE_URL}/refresh",
            json={"refresh_token": access_token},
        )
        print("Status:", res_bad_refresh.status_code)
        print("Body:", res_bad_refresh.json())
        assert res_bad_refresh.status_code in [401, 422]

        print("\n--- ۷. تست اعتبارسنجی پسورد ضعیف در Pydantic (۴۲۲) ---")
        res_weak = await client.post(
            f"{BASE_URL}/register",
            json={"email": f"weak_{unique_suffix}@hesabi.dev", "password": "123"},
        )
        print("Status:", res_weak.status_code)
        print("Body:", res_weak.json())
        assert res_weak.status_code == 422

        print("\nAll 7 Auth smoke tests passed successfully.")


if __name__ == "__main__":
    asyncio.run(run_auth_tests())
