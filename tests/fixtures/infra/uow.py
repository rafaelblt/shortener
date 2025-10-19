import pytest_asyncio

from shortener.infra.db.sqlalchemy_uow import SQLAlchemyUnitOfWork


@pytest_asyncio.fixture
async def sqlalchemy_uow(sqlalchemy_session):
    uow = SQLAlchemyUnitOfWork(sqlalchemy_session)
    return uow
