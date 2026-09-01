from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import v1_router
from app.db.database import engine
from app.errors.handlers import register_exception_handlers
from app.middleware import register_middlewares


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

register_middlewares(app)

register_exception_handlers(app)

app.include_router(v1_router)
