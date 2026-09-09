from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import v1_router
from app.db.database import engine
from app.errors.handlers import register_exception_handlers
from app.middleware import register_middlewares

tags_metadata = [
    {
        "name": "Categories",
        "description": "Manage financial categories and set monthly budget goals.",
    },
    {
        "name": "Transactions",
        "description": "Record and manage income and expense transactions.",
    },
    {
        "name": "Compute",
        "description": "Calculate financial rollups, overall summaries, and category balance,",
    },
    {
        "name": "Auth",
        "description": "User registration, authentication, and JWT token management.",
    },
    {
        "name": "Users",
        "description": "Operation on authenticated user profiles,",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="Hesabi API",
    description="A comprehensive Personal Financial Management and Budget Tracking API.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

register_middlewares(app)

register_exception_handlers(app)

app.include_router(v1_router)
