from typing import Final

from aio_pika.abc import AbstractConnection

from shortener.consumer.topology import declare_queue
from shortener.consumer.user_deleted_handler import UserDeletedHandler


# The handler holds a message while it waits to requeue it, so one at a time
# keeps the others in the queue, free for another consumer.
PREFETCH_COUNT: Final = 1


async def consume(connection: AbstractConnection, handler: UserDeletedHandler) -> None:
    """
    Starts consuming the queue of the service on a channel of the connection,
    and returns. The messages are handled until the connection is closed.
    See docs/architecture/consumer.md#consuming
    """
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=PREFETCH_COUNT)
    queue = await declare_queue(channel)
    await queue.consume(handler.handle)
