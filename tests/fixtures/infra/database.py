import asyncio

from collections.abc import AsyncIterator, Callable, Iterator
from typing import Any

import pytest

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Connection, MetaData, delete, make_url, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testcontainers.community.postgres import PostgresContainer

from shortener.domain import ShortURL
from shortener.infra.db.migrations import apply_migrations
from shortener.infra.db.shorturl_repository import SQLAlchemyShortURLReader
from shortener.infra.db.tables import metadata, shorturls
from shortener.infra.db.unit_of_work import SQLAlchemyUnitOfWork


POSTGRES_IMAGE = "postgres:17-alpine"
EMPTY_DATABASE = "empty"


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    """
    A Postgres in a container, with the migrations applied. The whole session
    shares it, and the engine fixture empties it before each test.
    """
    with PostgresContainer(POSTGRES_IMAGE, driver="asyncpg") as postgres:
        url = postgres.get_connection_url()
        asyncio.run(apply_migrations(url))
        yield url


@pytest.fixture
async def empty_database_url(database_url: str) -> AsyncIterator[str]:
    """A database without the migrations, beside the one of database_url."""
    engine = create_async_engine(database_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as connection:
        await connection.execute(text(f"CREATE DATABASE {EMPTY_DATABASE}"))
    yield (
        make_url(database_url)
        .set(database=EMPTY_DATABASE)
        .render_as_string(hide_password=False)
    )
    async with engine.connect() as connection:
        await connection.execute(text(f"DROP DATABASE {EMPTY_DATABASE} WITH (FORCE)"))
    await engine.dispose()


@pytest.fixture
async def engine(database_url: str) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(database_url)
    async with engine.begin() as connection:
        await connection.execute(delete(shorturls))
    yield engine
    await engine.dispose()


@pytest.fixture
def uow(engine: AsyncEngine) -> SQLAlchemyUnitOfWork:
    return SQLAlchemyUnitOfWork(engine)


@pytest.fixture
def reader(engine: AsyncEngine) -> SQLAlchemyShortURLReader:
    return SQLAlchemyShortURLReader(engine)


@pytest.fixture
async def stored_shorturl(
    uow: SQLAlchemyUnitOfWork, normal_shorturl: ShortURL
) -> ShortURL:
    await store(uow, normal_shorturl)
    return normal_shorturl


async def store(uow: SQLAlchemyUnitOfWork, *shorturls: ShortURL) -> None:
    """Adds the short URLs in a transaction, and commits it."""
    async with uow.begin() as transaction:
        for shorturl in shorturls:
            (await transaction.shorturls.add(shorturl)).unwrap()
        await transaction.commit()


async def differences_from_the_tables(
    database_url: str, tables: MetaData = metadata
) -> list[Any]:
    """
    How the database differs from the tables, by default the ones tables.py
    describes, which is nothing once it is migrated.
    """
    return await _run_on(
        database_url,
        lambda connection: compare_metadata(
            MigrationContext.configure(connection), tables
        ),
    )


async def reflect_tables(database_url: str) -> MetaData:
    """The tables the database has now, to compare it with them later."""
    return await _run_on(database_url, _reflect_tables)


async def _run_on[T](database_url: str, function: Callable[[Connection], T]) -> T:
    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as connection:
            return await connection.run_sync(function)
    finally:
        await engine.dispose()


def _reflect_tables(connection: Connection) -> MetaData:
    tables = MetaData()
    tables.reflect(connection)
    return tables
