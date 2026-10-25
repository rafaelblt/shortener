import asyncio

from collections.abc import Awaitable, Callable
from datetime import datetime

import pytest

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from shortener.domain import ShortURL, ShortURLID, Slug, UserID
from shortener.infra.db.shorturl_repository import SQLAlchemyShortURLReader
from shortener.infra.db.unit_of_work import SQLAlchemyUnitOfWork
from shortener.use_cases.shorturl_repository import ShortURLRepository
from shortener.use_cases.unavailable_error import UnavailableError
from tests.fixtures.infra.database import store


UNREACHABLE_DATABASE_URL = "postgresql+asyncpg://user:password@127.0.0.1:1/database"

type Read = Callable[[ShortURLRepository, ShortURL], Awaitable[object]]

READS = [
    pytest.param(
        lambda shorturls, shorturl: shorturls.get_by_id(shorturl.id), id="get_by_id"
    ),
    pytest.param(
        lambda shorturls, shorturl: shorturls.get_by_slug(shorturl.slug),
        id="get_by_slug",
    ),
    pytest.param(
        lambda shorturls, shorturl: shorturls.list_by_owner(
            shorturl.owner_id, limit=10, after=None
        ),
        id="list_by_owner",
    ),
]


async def wait_for_a_lock(engine: AsyncEngine, task: asyncio.Task[object]) -> None:
    """Returns once a session of the database waits for a lock, or the task ends."""
    async with asyncio.timeout(10):
        while not task.done():
            async with engine.connect() as connection:
                waiting = await connection.scalar(
                    text(
                        "SELECT count(*) FROM pg_stat_activity "
                        "WHERE datname = current_database() "
                        "AND wait_event_type = 'Lock'"
                    )
                )
            if waiting:
                return
            await asyncio.sleep(0.01)


async def read_by_id(uow: SQLAlchemyUnitOfWork, id: ShortURLID) -> ShortURL | None:
    async with uow.begin() as transaction:
        return await transaction.shorturls.get_by_id(id)


async def resolve(uow: SQLAlchemyUnitOfWork, id: ShortURLID, now: datetime) -> None:
    async with uow.begin() as transaction:
        shorturl = await transaction.shorturls.get_by_id(id)
        assert shorturl is not None
        shorturl.resolve(now).unwrap()
        (await transaction.shorturls.save(shorturl)).unwrap()
        await transaction.commit()


async def remove_by_owner(
    uow: SQLAlchemyUnitOfWork, owner_id: UserID, limit: int
) -> int:
    async with uow.begin() as transaction:
        removed = await transaction.shorturls.remove_by_owner(owner_id, limit)
        await transaction.commit()
    return removed


async def test_commit_makes_the_writes_of_the_transaction_permanent(
    uow: SQLAlchemyUnitOfWork,
    reader: SQLAlchemyShortURLReader,
    normal_shorturl: ShortURL,
):
    async with uow.begin() as transaction:
        await transaction.shorturls.add(normal_shorturl)
        await transaction.commit()

    assert await reader.get_by_id(normal_shorturl.id) is not None


async def test_leaving_the_block_without_committing_rolls_the_writes_back(
    uow: SQLAlchemyUnitOfWork,
    reader: SQLAlchemyShortURLReader,
    normal_shorturl: ShortURL,
):
    async with uow.begin() as transaction:
        await transaction.shorturls.add(normal_shorturl)

    assert await reader.get_by_id(normal_shorturl.id) is None


async def test_leaving_the_block_by_an_exception_rolls_the_writes_back(
    uow: SQLAlchemyUnitOfWork,
    reader: SQLAlchemyShortURLReader,
    normal_shorturl: ShortURL,
):
    # The block raises on purpose, and pytest.raises checks that begin()
    # doesn't swallow the exception.
    with pytest.raises(RuntimeError):  # noqa: PT012
        async with uow.begin() as transaction:
            await transaction.shorturls.add(normal_shorturl)
            raise RuntimeError

    assert await reader.get_by_id(normal_shorturl.id) is None


@pytest.mark.parametrize("read", READS)
async def test_a_read_through_a_transaction_waits_for_another_that_read_it_to_end(
    uow: SQLAlchemyUnitOfWork,
    engine: AsyncEngine,
    stored_shorturl: ShortURL,
    read: Read,
):
    async with uow.begin() as transaction:
        await read(transaction.shorturls, stored_shorturl)
        waiting_read = asyncio.create_task(read_by_id(uow, stored_shorturl.id))
        await wait_for_a_lock(engine, waiting_read)

        assert not waiting_read.done()

    assert await waiting_read is not None


async def test_a_read_that_waited_reads_what_the_other_transaction_wrote(
    uow: SQLAlchemyUnitOfWork,
    engine: AsyncEngine,
    reader: SQLAlchemyShortURLReader,
    stored_shorturl: ShortURL,
    now: datetime,
):
    # Two concurrent resolutions of the same short URL, as in issue #7.
    async with uow.begin() as transaction:
        shorturl = await transaction.shorturls.get_by_id(stored_shorturl.id)
        assert shorturl is not None
        waiting_resolution = asyncio.create_task(resolve(uow, shorturl.id, now))
        await wait_for_a_lock(engine, waiting_resolution)
        shorturl.resolve(now).unwrap()
        (await transaction.shorturls.save(shorturl)).unwrap()
        await transaction.commit()
    await waiting_resolution

    resolved = await reader.get_by_id(stored_shorturl.id)
    assert resolved is not None
    assert resolved.resolution_count == 2


async def test_a_read_that_waited_returns_none_when_the_other_transaction_removed_it(
    uow: SQLAlchemyUnitOfWork, engine: AsyncEngine, stored_shorturl: ShortURL
):
    async with uow.begin() as transaction:
        shorturl = await transaction.shorturls.get_by_id(stored_shorturl.id)
        assert shorturl is not None
        waiting_read = asyncio.create_task(read_by_id(uow, shorturl.id))
        await wait_for_a_lock(engine, waiting_read)
        await transaction.shorturls.remove(shorturl)
        await transaction.commit()

    assert await waiting_read is None


async def test_remove_by_owner_that_waited_takes_others_for_the_ones_removed_meanwhile(
    uow: SQLAlchemyUnitOfWork,
    engine: AsyncEngine,
    reader: SQLAlchemyShortURLReader,
    normal_shorturl: ShortURL,
    other_shorturl: ShortURL,
    biggest_shorturl: ShortURL,
    owner_id: UserID,
):
    await store(uow, normal_shorturl, other_shorturl, biggest_shorturl)

    async with uow.begin() as transaction:
        await transaction.shorturls.remove(normal_shorturl)
        await transaction.shorturls.remove(other_shorturl)
        # Only one short URL of the owner is free, so a batch of two waits
        # for the ones this transaction removes.
        waiting_removal = asyncio.create_task(remove_by_owner(uow, owner_id, 2))
        await wait_for_a_lock(engine, waiting_removal)
        await transaction.commit()

    assert await waiting_removal == 1
    assert await reader.list_by_owner(owner_id, 10, None) == []


async def test_a_read_by_slug_that_waited_returns_none_when_the_slug_changed(
    uow: SQLAlchemyUnitOfWork, engine: AsyncEngine, stored_shorturl: ShortURL
):
    async def read_by_old_slug() -> ShortURL | None:
        async with uow.begin() as other:
            return await other.shorturls.get_by_slug(stored_shorturl.slug)

    async with uow.begin() as transaction:
        shorturl = await transaction.shorturls.get_by_id(stored_shorturl.id)
        assert shorturl is not None
        waiting_read = asyncio.create_task(read_by_old_slug())
        await wait_for_a_lock(engine, waiting_read)
        shorturl.change_slug(Slug("new-slug"))
        (await transaction.shorturls.save(shorturl)).unwrap()
        await transaction.commit()

    assert await waiting_read is None


async def test_begin_raises_unavailable_when_the_database_is_unreachable():
    engine = create_async_engine(UNREACHABLE_DATABASE_URL)
    try:
        with pytest.raises(UnavailableError) as raised:
            async with SQLAlchemyUnitOfWork(engine).begin():
                pass
        assert isinstance(raised.value.__cause__, OSError)
    finally:
        await engine.dispose()


async def test_a_read_raises_unavailable_when_the_wait_for_a_lock_runs_out(
    uow: SQLAlchemyUnitOfWork, database_url: str, stored_shorturl: ShortURL
):
    impatient_engine = create_async_engine(
        database_url, connect_args={"server_settings": {"lock_timeout": "100ms"}}
    )
    try:
        async with uow.begin() as transaction:
            await transaction.shorturls.get_by_id(stored_shorturl.id)
            with pytest.raises(UnavailableError) as raised:
                await read_by_id(
                    SQLAlchemyUnitOfWork(impatient_engine), stored_shorturl.id
                )
        assert isinstance(raised.value.__cause__, DBAPIError)
    finally:
        await impatient_engine.dispose()
