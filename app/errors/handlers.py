from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.errors.exceptions import AppError

app = FastAPI()


@app.exception_handler(AppError)
async def custom_exception_errors(
        request: Request,
        exc: AppError
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "message": exc.message
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_errors(
        request: Request,
        exc: RequestValidationError
):
    errors = []

    for error in exc.errors():
        field_path = "->".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field_path,
            "message": error["msg"]
        })

    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid request payload or query parameters",
            "errors": errors,
            "body": exc.body,
        })
    )

@app.exception_handler(StarletteHTTPException)
async def http_errors(
        request: Request,
        exc: StarletteHTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": f"HTTP_{exc.status_code}",
            "message": str(exc.detail)
        },
        headers=exc.headers,
    )

