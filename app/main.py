from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.models import engine
from app.middleware import register_middlewares

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

register_middlewares(app)


