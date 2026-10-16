import pytest

from asyncpg.exceptions import InvalidCatalogNameError
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from shortener.infra.db.health_check import SQLAlchemyHealthCheck
from shortener.use_cases.unavailable_error import UnavailableError


UNREACHABLE_DATABASE_URL = "postgresql+asyncpg://user:password@127.0.0.1:1/database"


async def test_check_passes_when_the_database_answers(engine: AsyncEngine):
    await SQLAlchemyHealthCheck(engine).check()


async def test_check_raises_unavailable_when_the_database_is_unreachable():
    engine = create_async_engine(UNREACHABLE_DATABASE_URL)
    try:
        with pytest.raises(UnavailableError) as raised:
            await SQLAlchemyHealthCheck(engine).check()
        assert isinstance(raised.value.__cause__, OSError)
    finally:
        await engine.dispose()


async def test_check_raises_the_errors_that_trying_again_would_not_fix(
    database_url: str,
):
    engine = create_async_engine(make_url(database_url).set(database="missing"))
    try:
        with pytest.raises(InvalidCatalogNameError):
            await SQLAlchemyHealthCheck(engine).check()
    finally:
        await engine.dispose()
