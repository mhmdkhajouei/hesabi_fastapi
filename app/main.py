from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)



