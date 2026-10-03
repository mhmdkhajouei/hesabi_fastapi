import uuid

import pytest
from httpx import AsyncClient

from app.config import settings


class TestSecurityAndTracingMiddleware:
    async def test_middleware_request_id_verify(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/auth/login")
        assert "X-Request-Id" in response.headers

        generated_id = response.headers["X-Request-Id"]
        uuid_obj = uuid.UUID(generated_id, version=4)

        assert str(uuid_obj) == generated_id

    async def test_middleware_custom_request_id(self, async_client: AsyncClient):
        custom_request_id = str(uuid.uuid4())
        headers = {"X-Request-Id": custom_request_id}

        response = await async_client.get("/api/v1/auth/login", headers=headers)

        assert response.headers["X-Request-Id"] == custom_request_id

    async def test_security_headers_injected(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/auth/login")

        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"


CONFIGURED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]


class TestCORSMiddleware:
    @pytest.mark.parametrize("allowed_origin", settings.cors_origins)
    @pytest.mark.parametrize("method", CONFIGURED_METHODS)
    async def test_cors_preflight_all_configured_methods_and_origins(
        self, async_client: AsyncClient, allowed_origin: str, method: str
    ):
        custom_header = "X-Custom-Client-Header"
        headers = {
            "Origin": allowed_origin,
            "Access-Control-Request-Method": method,
            "Access-Control-Request-Headers": f"Authorization, Content-Type {custom_header}",
        }

        response = await async_client.options("/api/v1/auth/login", headers=headers)

        assert response.status_code == 200
        assert response.headers.get("Access-Control-Allow-Origin") == allowed_origin
        assert response.headers.get("Access-Control-Allow-Credentials") == "true"
        assert response.headers.get("Access-Control-Max-Age") == "600"

        returned_methods = [
            m.strip()
            for m in response.headers.get("Access-Control-Allow-Methods", "").split(",")
        ]
        assert set(returned_methods) == set(CONFIGURED_METHODS)

        returned_headers = response.headers.get("Access-Control-Allow-Headers", "")
        assert "Authorization" in returned_headers
        assert custom_header in returned_headers

    @pytest.mark.parametrize("allowed_origin", settings.cors_origins)
    async def test_cors_preflight_disallowed_method_rejected(
        self, async_client: AsyncClient, allowed_origin: str
    ):
        headers = {
            "Origin": allowed_origin,
            "Access-Control-Request-Method": "PATCH",
        }
        response = await async_client.options("/api/v1/auth/login", headers=headers)

        assert response.status_code == 400
        assert response.text == "Disallowed CORS method"

        allowed_methods = response.headers.get("Access-Control-Allow-Methods", "")
        assert "PATCH" not in allowed_methods

    async def test_cors_simple_get_exposed_headers(self, async_client: AsyncClient):
        allowed_origin = settings.cors_origins[0]
        headers = {"Origin": allowed_origin}

        response = await async_client.get("/api/v1/auth/login", headers=headers)

        assert response.headers.get("Access-Control-Allow-Origin") == allowed_origin
        assert response.headers.get("Access-Control-Allow-Credentials") == "true"
        assert response.headers.get("Access-Control-Expose-Headers") == "X-Request-Id"
