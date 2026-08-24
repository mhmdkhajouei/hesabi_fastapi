from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import  engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)



