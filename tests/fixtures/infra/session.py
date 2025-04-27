import pytest_asyncio

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from shortener.infra.db.models import Base


@pytest_asyncio.fixture
async def db_session():
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    test_database_engine = create_async_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestSession = sessionmaker(bind=test_database_engine, class_=AsyncSession)

    async with test_database_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSession() as session:
        yield session
    
    async with test_database_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_database_engine.dispose()
