from app.api.api import api_router
from app.db.session import setup_db

from fastapi import FastAPI
from typing import AsyncGenerator
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    setup_db(app)
    yield
    app.state.db_engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api")
