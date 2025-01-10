from app.core.config import setting

from fastapi import FastAPI, Request
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine


def setup_db(app: FastAPI) -> None:
    engine = create_async_engine(setting.get_postgres_uri, echo=False)
    session = async_sessionmaker(engine, expire_on_commit=False)
    app.state.db_engine = engine
    app.state.db_session = session


async def get_db(request: Request):
    session = request.app.state.db_session()
    try:
        yield session
    finally:
        session.commit()
        session.close()
