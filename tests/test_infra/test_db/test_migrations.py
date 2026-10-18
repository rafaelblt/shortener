import asyncio
import sys

from collections.abc import AsyncIterator

import pytest

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from shortener.infra.db.migrations import (
    MIGRATIONS_LOCK_KEY,
    UnexpectedMigrationsError,
    apply_migrations,
    check_migrations,
)
from tests.fixtures.infra.database import differences_from_the_tables
from tests.utils.text_helpers import assert_mentions


# Applies the migrations to the database of the URL it receives, as the
# process of a replica of the service would.
APPLY_MIGRATIONS = """
import asyncio, sys
from shortener.infra.db.migrations import apply_migrations
asyncio.run(apply_migrations(sys.argv[1]))
"""


@pytest.fixture
async def empty_engine(empty_database_url: str) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(empty_database_url)
    yield engine
    await engine.dispose()


async def waiting_for_the_lock(connection: AsyncConnection) -> int:
    """How many sessions wait for an advisory lock of the database."""
    result = await connection.execute(
        text(
            "SELECT count(*) FROM pg_locks JOIN pg_database"
            " ON pg_locks.database = pg_database.oid"
            " WHERE datname = current_database()"
            " AND locktype = 'advisory' AND NOT granted"
        )
    )
    return result.scalar_one()


async def test_the_migrations_create_the_tables_as_tables_describes_them(
    database_url: str,
):
    assert await differences_from_the_tables(database_url) == []


async def test_apply_migrations_migrates_an_empty_database(empty_database_url: str):
    await apply_migrations(empty_database_url)
    assert await differences_from_the_tables(empty_database_url) == []


async def test_apply_migrations_of_a_migrated_database_changes_nothing(
    database_url: str,
):
    await apply_migrations(database_url)
    assert await differences_from_the_tables(database_url) == []


async def test_processes_that_migrate_at_once_wait_for_each_other_and_all_succeed(
    empty_database_url: str,
):
    engine = create_async_engine(empty_database_url)
    lock = {"key": MIGRATIONS_LOCK_KEY}
    processes: list[asyncio.subprocess.Process] = []
    try:
        async with engine.connect() as holder:
            # While the lock is held, every process waits for it, so they all
            # go on at once when it is released.
            await holder.execute(text("SELECT pg_advisory_lock(:key)"), lock)
            await holder.commit()
            # The processes inherit the environment, which has what measures
            # their coverage.
            for _ in range(3):
                processes.append(
                    await asyncio.create_subprocess_exec(
                        sys.executable, "-c", APPLY_MIGRATIONS, empty_database_url
                    )
                )
            async with asyncio.timeout(30):
                while await waiting_for_the_lock(holder) < len(processes):
                    await asyncio.sleep(0.05)
            await holder.execute(text("SELECT pg_advisory_unlock(:key)"), lock)
            await holder.commit()
            async with asyncio.timeout(30):
                return_codes = [await process.wait() for process in processes]
    finally:
        for process in processes:
            if process.returncode is None:
                process.kill()
                await process.wait()
        await engine.dispose()

    assert return_codes == [0] * len(processes)
    assert await differences_from_the_tables(empty_database_url) == []


async def test_check_migrations_passes_for_a_migrated_database(engine: AsyncEngine):
    await check_migrations(engine)


async def test_check_migrations_raises_for_a_database_without_migrations(
    empty_engine: AsyncEngine,
):
    with pytest.raises(UnexpectedMigrationsError) as raised:
        await check_migrations(empty_engine)
    assert raised.value.applied == ()
    assert_mentions(str(raised.value), *raised.value.expected)


async def test_check_migrations_raises_for_a_migration_the_code_doesnt_know(
    empty_engine: AsyncEngine,
):
    async with empty_engine.begin() as connection:
        await connection.execute(
            text("CREATE TABLE alembic_version (version_num varchar(32) PRIMARY KEY)")
        )
        await connection.execute(
            text("INSERT INTO alembic_version VALUES ('a-later-migration')")
        )

    with pytest.raises(UnexpectedMigrationsError) as raised:
        await check_migrations(empty_engine)
    assert raised.value.applied == ("a-later-migration",)
    assert_mentions(str(raised.value), "a-later-migration", *raised.value.expected)
