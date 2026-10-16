import asyncio

from datetime import timedelta

import pytest

from sqlalchemy import text
from sqlalchemy.exc import TimeoutError as PoolTimeoutError

from shortener.bootstrap.database import database_engine
from shortener.bootstrap.settings import DatabaseSettings


async def test_database_engine_sets_the_lock_and_statement_timeouts_of_its_connections(
    database_url: str,
):
    # Postgres keeps them in whole milliseconds, so a fraction rounds up.
    engine = database_engine(
        DatabaseSettings(
            database_url,
            lock_timeout=timedelta(microseconds=100),
            statement_timeout=timedelta(seconds=1.5),
        )
    )
    try:
        async with engine.connect() as connection:
            settings = await connection.execute(
                text(
                    "SELECT name, setting FROM pg_settings"
                    " WHERE name IN ('lock_timeout', 'statement_timeout')"
                )
            )
            assert {row.name: row.setting for row in settings} == {
                "lock_timeout": "1",
                "statement_timeout": "1500",
            }
    finally:
        await engine.dispose()


async def test_database_engine_waits_for_a_free_connection_up_to_the_pool_timeout(
    database_url: str,
):
    engine = database_engine(
        DatabaseSettings(
            database_url,
            pool_size=1,
            max_overflow=1,
            pool_timeout=timedelta(milliseconds=100),
        )
    )
    try:
        async with engine.connect(), engine.connect():
            # The default pool timeout, 30 seconds, would outlast this one.
            async with asyncio.timeout(5):
                with pytest.raises(PoolTimeoutError):
                    await engine.connect().start()
    finally:
        await engine.dispose()


async def test_database_engine_waits_to_connect_up_to_the_connect_timeout(
    silent_server: str,
):
    engine = database_engine(
        DatabaseSettings(
            f"postgresql+asyncpg://user:password@{silent_server}/database",
            connect_timeout=timedelta(milliseconds=100),
        )
    )
    try:
        # The default timeout of asyncpg, 60 seconds, would outlast this one.
        async with asyncio.timeout(5):
            with pytest.raises(TimeoutError):
                await engine.connect().start()
    finally:
        await engine.dispose()
