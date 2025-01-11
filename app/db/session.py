from typing import AsyncGenerator

from fastapi import FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import setting


def setup_db(app: FastAPI) -> None:
    engine = create_async_engine(setting.get_postgres_uri, echo=False)
    session = async_sessionmaker(engine, expire_on_commit=False)
    app.state.db_engine = engine
    app.state.db_session = session


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = request.app.state.db_session()
    try:
        yield session
    finally:
        await session.commit()
        await session.close()
