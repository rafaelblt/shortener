import pytest_asyncio

from shortener.infra.db.repositories import (
    SQLAlchemyShortURLRepository,
    SQLAlchemyUserRepository,
    SQLAlchemyPlanRepository,
)


@pytest_asyncio.fixture
async def sqlalchemy_shorturl_repository(sqlalchemy_session):
    return SQLAlchemyShortURLRepository(sqlalchemy_session)


@pytest_asyncio.fixture
async def sqlalchemy_user_repository(sqlalchemy_session):
    return SQLAlchemyUserRepository(sqlalchemy_session)


@pytest_asyncio.fixture
async def sqlalchemy_plan_repository(sqlalchemy_session):
    return SQLAlchemyPlanRepository(sqlalchemy_session)
