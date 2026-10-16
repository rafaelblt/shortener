import aio_pika
import asyncio
import logging
import signal

from shortener.bootstrap.app import database_engine
from shortener.bootstrap.settings import ConsumerSettings
from shortener.consumer.consumer import consume
from shortener.consumer.user_deleted_handler import UserDeletedHandler
from shortener.infra.db.unit_of_work import SQLAlchemyUnitOfWork
from shortener.use_cases.delete_shorturls_of_user import DeleteShortURLsOfUser


logger = logging.getLogger(__name__)


async def run_consumer(
    stop: asyncio.Event, settings: ConsumerSettings | None = None
) -> None:
    """
    Consumes the events until stop is set, with the settings, or with the ones
    of the environment variables when there are none.
    See docs/bootstrap.md#the-consumer

    Raises:
        SettingsError: The environment variables don't make valid settings.
        aio_pika.exceptions.AMQPConnectionError: RabbitMQ can't be reached
            when the consumer starts.
    """
    if settings is None:
        settings = ConsumerSettings.from_environment()

    engine = database_engine(settings.database)
    handler = UserDeletedHandler(DeleteShortURLsOfUser(SQLAlchemyUnitOfWork(engine)))
    try:
        connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        async with connection:
            await consume(connection, handler)
            logger.info("Consuming the events of deleted users")
            await stop.wait()
    finally:
        await engine.dispose()


def main() -> None:
    """Runs the consumer until the process gets SIGINT or SIGTERM."""
    logging.basicConfig(level=logging.INFO)
    asyncio.run(_run_until_signaled())


async def _run_until_signaled() -> None:
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signal_number in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signal_number, stop.set)
    await run_consumer(stop)


if __name__ == "__main__":
    main()
