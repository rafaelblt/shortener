import asyncio

from unittest.mock import NonCallableMagicMock, create_autospec

from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractIncomingMessage

from shortener.consumer.consumer import consume
from shortener.consumer.topology import QUEUE
from shortener.consumer.user_deleted_handler import UserDeletedHandler
from tests.fixtures.consumer.rabbitmq import count_ready, publish


def handler_that_keeps(messages: asyncio.Queue[AbstractIncomingMessage]) -> NonCallableMagicMock:
    """A handler that keeps each message, without acknowledging it."""
    handler = create_autospec(UserDeletedHandler, instance=True)
    handler.handle.side_effect = messages.put
    return handler


async def test_consume_hands_the_messages_of_the_queue_to_the_handler(
    connection: AbstractConnection, channel: AbstractChannel
):
    messages: asyncio.Queue[AbstractIncomingMessage] = asyncio.Queue()

    await consume(connection, handler_that_keeps(messages))
    await publish(channel, b"event")

    async with asyncio.timeout(5):
        message = await messages.get()
    assert message.body == b"event"


async def test_consume_hands_one_message_at_a_time_until_it_is_acknowledged(
    connection: AbstractConnection, channel: AbstractChannel
):
    messages: asyncio.Queue[AbstractIncomingMessage] = asyncio.Queue()
    await consume(connection, handler_that_keeps(messages))

    await publish(channel, b"first")
    await publish(channel, b"second")
    async with asyncio.timeout(5):
        first = await messages.get()

    assert first.body == b"first"
    assert messages.empty()
    assert await count_ready(channel, QUEUE) == 1
