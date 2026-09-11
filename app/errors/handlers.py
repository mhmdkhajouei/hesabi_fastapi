import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.errors.exceptions import AppError

logger = logging.getLogger(__name__)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    if not isinstance(exc, AppError):
        raise exc

    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "message": exc.message,
        },
        headers=headers,
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors: list[dict[str, Any]] = []
    for error in exc.errors():
        field_path = "->".join(str(loc) for loc in error["loc"])
        errors.append(
            {
                "field": field_path,
                "message": error["msg"],
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid request payload or query parameters",
            "errors": errors,
        },
    )


async def http_error_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": f"HTTP_{exc.status_code}",
            "message": str(exc.detail),
        },
        headers=exc.headers,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


async def jwt_exception_handler(request: Request, exc: PyJWTError) -> JSONResponse:
    error_code = (
        "TOKEN_EXPIRED" if isinstance(exc, ExpiredSignatureError) else "INVALID_TOKEN"
    )
    raw_message = exc.args[0] if exc.args else str(exc)

    logger.warning(
        f"JWT Auth Failed | Type: {exc.__class__.__name__} | "
        f"Detail: {raw_message} | Path: {request.url.path} | "
        f"Client IP: {request.client.host if request.client else 'unknown'}"
    )

    return JSONResponse(
        status_code=401,
        content={
            "success": False,
            "error_code": error_code,
            "message": raw_message,
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.exception_handler(AppError)(app_error_handler)
    app.exception_handler(RequestValidationError)(validation_error_handler)
    app.exception_handler(StarletteHTTPException)(http_error_handler)
    app.exception_handler(Exception)(unhandled_exception_handler)
    app.exception_handler(PyJWTError)(jwt_exception_handler)
