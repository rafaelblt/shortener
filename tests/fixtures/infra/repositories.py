import pytest_asyncio

from shortener.infra.db.repositories import (
    SQLAlchemyShortURLRepository,
    SQLAlchemyUserRepository,
    SQLAlchemyPlanRepository
)


@pytest_asyncio.fixture
async def sqlalchemy_shorturl_repository(db_session):
    return SQLAlchemyShortURLRepository(db_session)


@pytest_asyncio.fixture
async def sqlalchemy_user_repository(db_session):
    return SQLAlchemyUserRepository(db_session)


@pytest_asyncio.fixture
async def sqlalchemy_plan_repository(db_session):
    return SQLAlchemyPlanRepository(db_session)
