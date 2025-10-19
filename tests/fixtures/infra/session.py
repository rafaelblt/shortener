import os
import pytest_asyncio

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from shortener.infra.db.models import Base


@pytest_asyncio.fixture
async def db_session(sqlalchemy_session):
    return sqlalchemy_session


@pytest_asyncio.fixture
async def sqlalchemy_engine(tmp_path):
    db_file = tmp_path / "test_db.sqlite"
    TEST_DATABASE_URL = f"sqlite+aiosqlite:///{db_file}"
    engine = create_async_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    if db_file.exists():
        os.remove(db_file)


@pytest_asyncio.fixture
async def sqlalchemy_session_factory(sqlalchemy_engine):
    return sessionmaker(
        bind=sqlalchemy_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def sqlalchemy_session(sqlalchemy_session_factory):
    async with sqlalchemy_session_factory() as session:
        yield session
