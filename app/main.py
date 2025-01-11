from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core.config import setting
from app.db.session import setup_db
from app.services.chat.runnable import setup_runnable


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    setup_db(app)
    setup_runnable(app)
    yield
    app.state.runnable.dispose()
    app.state.db_engine.dispose()


app = FastAPI(lifespan=lifespan)

if setting.allow_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=setting.allow_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api")
