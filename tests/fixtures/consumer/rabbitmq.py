import aio_pika
import asyncio
import pytest

from collections.abc import AsyncIterator, Iterator

from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractIncomingMessage
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

from shortener.consumer.topology import (
    DEAD_LETTER_QUEUE,
    EXCHANGE,
    QUEUE,
    ROUTING_KEY,
)


RABBITMQ_IMAGE = "rabbitmq:4-alpine"
AMQP_PORT = 5672


@pytest.fixture(scope="session")
def rabbitmq_url() -> Iterator[str]:
    """
    A RabbitMQ in a container. The whole session shares it, and the
    connection fixture deletes the queues and the exchange of the service
    before each test.
    """
    container = (
        DockerContainer(RABBITMQ_IMAGE)
        .with_env("RABBITMQ_DEFAULT_USER", "shortener")
        .with_env("RABBITMQ_DEFAULT_PASS", "shortener")
        .with_exposed_ports(AMQP_PORT)
        .waiting_for(LogMessageWaitStrategy("Server startup complete"))
    )
    with container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(AMQP_PORT)
        yield f"amqp://shortener:shortener@{host}:{port}/"


@pytest.fixture
async def connection(rabbitmq_url: str) -> AsyncIterator[AbstractConnection]:
    connection = await aio_pika.connect(rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        for queue in (QUEUE, DEAD_LETTER_QUEUE):
            await channel.queue_delete(queue)
        await channel.exchange_delete(EXCHANGE)
        await channel.close()
        yield connection


@pytest.fixture
async def channel(connection: AbstractConnection) -> AsyncIterator[AbstractChannel]:
    channel = await connection.channel()
    yield channel
    await channel.close()


async def publish(
    channel: AbstractChannel, body: bytes, routing_key: str = ROUTING_KEY
) -> None:
    """Publishes the body to the exchange of the events, which has to exist."""
    exchange = await channel.get_exchange(EXCHANGE)
    await exchange.publish(aio_pika.Message(body), routing_key=routing_key)


async def receive(channel: AbstractChannel, queue_name: str) -> AbstractIncomingMessage:
    """
    The next message of the queue, waiting up to 5 seconds for one. The
    message is left unacknowledged.
    """
    queue = await channel.get_queue(queue_name)
    async with asyncio.timeout(5):
        while (message := await queue.get(fail=False)) is None:
            await asyncio.sleep(0.05)
    return message


async def count_ready(channel: AbstractChannel, queue_name: str) -> int:
    """The messages of the queue waiting to be delivered."""
    queue = await channel.declare_queue(queue_name, passive=True)
    return queue.declaration_result.message_count or 0
