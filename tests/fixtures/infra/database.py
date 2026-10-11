import pytest

from collections.abc import AsyncIterator, Iterator
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testcontainers.community.postgres import PostgresContainer

from shortener.domain import ShortURL
from shortener.infra.db.shorturl_repository import SQLAlchemyShortURLReader
from shortener.infra.db.tables import shorturls
from shortener.infra.db.unit_of_work import SQLAlchemyUnitOfWork


POSTGRES_IMAGE = "postgres:17-alpine"
MIGRATIONS = Path(__file__).parents[3] / "alembic"


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    """
    A Postgres in a container, with the migrations applied. The whole session
    shares it, and the engine fixture empties it before each test.
    """
    with PostgresContainer(POSTGRES_IMAGE, driver="asyncpg") as postgres:
        url = postgres.get_connection_url()
        _migrate(url)
        yield url


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


def _migrate(url: str) -> None:
    config = Config()
    config.set_main_option("script_location", str(MIGRATIONS))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
