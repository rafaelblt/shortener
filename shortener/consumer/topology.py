from typing import Final

from aio_pika import ExchangeType
from aio_pika.abc import AbstractChannel, AbstractQueue


EXCHANGE: Final = "users"
ROUTING_KEY: Final = "user.deleted"
QUEUE: Final = "shortener.user-deleted"
DEAD_LETTER_QUEUE: Final = "shortener.user-deleted.dead"


async def declare_queue(channel: AbstractChannel) -> AbstractQueue:
    """
    Declares the exchange of the events, the queue of the service, bound to
    it, and the dead-letter queue, and returns the queue of the service.
    See docs/architecture/consumer.md#topology
    """
    exchange = await channel.declare_exchange(
        EXCHANGE, ExchangeType.TOPIC, durable=True
    )
    await channel.declare_queue(DEAD_LETTER_QUEUE, durable=True)
    # A rejected message goes, through the default exchange, which routes by
    # the name of the queue, to the dead-letter queue.
    queue = await channel.declare_queue(
        QUEUE,
        durable=True,
        arguments={
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": DEAD_LETTER_QUEUE,
        },
    )
    await queue.bind(exchange, ROUTING_KEY)
    return queue
