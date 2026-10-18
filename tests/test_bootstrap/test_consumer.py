import asyncio
import os
import signal
import sys

from dataclasses import replace
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from aio_pika.abc import AbstractChannel
from aio_pika.exceptions import AMQPConnectionError
from sqlalchemy.ext.asyncio import AsyncEngine

from shortener.bootstrap.consumer import run_consumer
from shortener.bootstrap.settings import ConsumerSettings, DatabaseSettings
from shortener.consumer.topology import declare_queue
from shortener.domain import ShortURL, Slug, TargetURL, UserID
from shortener.infra.db.migrations import UnexpectedMigrationsError
from shortener.infra.db.shorturl_repository import SQLAlchemyShortURLReader
from shortener.infra.db.unit_of_work import SQLAlchemyUnitOfWork
from tests.fixtures.consumer.rabbitmq import publish
from tests.fixtures.infra.database import differences_from_the_tables, store


UNREACHABLE_RABBITMQ_URL = "amqp://user:password@127.0.0.1:1/"


@pytest.fixture
def settings(database_url: str, rabbitmq_url: str) -> ConsumerSettings:
    return ConsumerSettings(
        database=DatabaseSettings(url=database_url), rabbitmq_url=rabbitmq_url
    )


@pytest.fixture
def stopped() -> asyncio.Event:
    """A stop that is already set, so the consumer stops once it starts."""
    stop = asyncio.Event()
    stop.set()
    return stop


@pytest.fixture
def engine_double(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """An engine, without a database to check when the consumer starts."""
    engine = Mock(dispose=AsyncMock())
    monkeypatch.setattr(
        "shortener.bootstrap.database.create_async_engine", Mock(return_value=engine)
    )
    monkeypatch.setattr("shortener.bootstrap.consumer.prepare_database", AsyncMock())
    return engine


async def wait_for_a_line(stream: asyncio.StreamReader, text: bytes) -> None:
    """Reads the lines of the stream until one has the text."""
    while line := await stream.readline():
        if text in line:
            return
    raise AssertionError(f"The stream ended without a line with {text!r}")


def shorturl_of(owner_id: UserID, slug: str, now: datetime) -> ShortURL:
    return ShortURL.create(
        slug=Slug(slug),
        target_url=TargetURL("https://example.com"),
        owner_id=owner_id,
        now=now,
    )


async def test_run_consumer_deletes_the_shorturls_of_the_user_of_each_event(
    settings: ConsumerSettings,
    engine: AsyncEngine,
    channel: AbstractChannel,
    owner_id: UserID,
    other_user_id: UserID,
    now: datetime,
):
    reader = SQLAlchemyShortURLReader(engine)
    shorturl_of_another_user = shorturl_of(other_user_id, "other-user", now)
    await store(
        SQLAlchemyUnitOfWork(engine),
        shorturl_of(owner_id, "owner", now),
        shorturl_of_another_user,
    )
    await declare_queue(channel)
    await publish(channel, f'{{"user_id": "{owner_id.value}"}}'.encode())

    stop = asyncio.Event()
    consuming = asyncio.create_task(run_consumer(stop, settings))
    try:
        async with asyncio.timeout(10):
            while await reader.list_by_owner(owner_id, 10, None):
                await asyncio.sleep(0.05)
    finally:
        stop.set()
        await consuming

    assert await reader.get_by_id(shorturl_of_another_user.id) is not None


async def test_run_consumer_returns_when_stop_is_set(
    settings: ConsumerSettings, stopped: asyncio.Event
):
    async with asyncio.timeout(10):
        await run_consumer(stopped, settings)


async def test_run_consumer_migrates_its_database_when_it_starts_if_set(
    settings: ConsumerSettings, stopped: asyncio.Event, empty_database_url: str
):
    database = DatabaseSettings(empty_database_url, migrate_on_start=True)

    await run_consumer(stopped, replace(settings, database=database))

    assert await differences_from_the_tables(empty_database_url) == []


async def test_run_consumer_raises_when_its_database_isnt_migrated(
    settings: ConsumerSettings, stopped: asyncio.Event, empty_database_url: str
):
    database = DatabaseSettings(empty_database_url)

    with pytest.raises(UnexpectedMigrationsError):
        await run_consumer(stopped, replace(settings, database=database))
    assert await differences_from_the_tables(empty_database_url) != []


async def test_run_consumer_without_settings_reads_them_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
    settings: ConsumerSettings,
    stopped: asyncio.Event,
):
    monkeypatch.setenv("DATABASE_URL", settings.database.url)
    monkeypatch.setenv("RABBITMQ_URL", settings.rabbitmq_url)

    async with asyncio.timeout(10):
        await run_consumer(stopped)


async def test_run_consumer_disposes_its_engine_when_it_stops(
    settings: ConsumerSettings,
    stopped: asyncio.Event,
    engine_double: Mock,
):
    await run_consumer(stopped, settings)
    engine_double.dispose.assert_awaited_once()


async def test_run_consumer_raises_and_disposes_its_engine_when_rabbitmq_is_unreachable(
    settings: ConsumerSettings, stopped: asyncio.Event, engine_double: Mock
):
    unreachable = ConsumerSettings(
        database=settings.database, rabbitmq_url=UNREACHABLE_RABBITMQ_URL
    )

    with pytest.raises(AMQPConnectionError):
        await run_consumer(stopped, unreachable)
    engine_double.dispose.assert_awaited_once()


@pytest.mark.parametrize(
    "signal_number",
    [
        pytest.param(signal.SIGINT, id="SIGINT"),
        pytest.param(signal.SIGTERM, id="SIGTERM"),
    ],
)
async def test_main_consumes_until_the_process_gets_sigint_or_sigterm(
    settings: ConsumerSettings, signal_number: signal.Signals
):
    # The process inherits the environment, which has what measures its
    # coverage.
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "shortener.bootstrap.consumer",
        env={
            **os.environ,
            "DATABASE_URL": settings.database.url,
            "RABBITMQ_URL": settings.rabbitmq_url,
        },
        stderr=asyncio.subprocess.PIPE,
    )
    assert process.stderr is not None
    try:
        async with asyncio.timeout(30):
            await wait_for_a_line(process.stderr, b"Consuming the events")
            process.send_signal(signal_number)
            await process.communicate()
    finally:
        if process.returncode is None:
            process.kill()
            await process.wait()

    assert process.returncode == 0
