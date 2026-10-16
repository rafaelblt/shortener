from aio_pika.abc import AbstractChannel

from shortener.consumer.topology import DEAD_LETTER_QUEUE, QUEUE, declare_queue
from tests.fixtures.consumer.rabbitmq import count_ready, publish, receive


async def test_declare_queue_returns_the_queue_of_the_service(channel: AbstractChannel):
    queue = await declare_queue(channel)
    assert queue.name == QUEUE


async def test_the_queue_receives_the_events_of_deleted_users(channel: AbstractChannel):
    await declare_queue(channel)

    await publish(channel, b"event")

    assert (await receive(channel, QUEUE)).body == b"event"


async def test_the_queue_does_not_receive_other_events(channel: AbstractChannel):
    await declare_queue(channel)

    await publish(channel, b"event", routing_key="user.created")
    await publish(channel, b"event")
    await receive(channel, QUEUE)

    assert await count_ready(channel, QUEUE) == 0


async def test_a_message_rejected_without_requeuing_goes_to_the_dead_letter_queue(
    channel: AbstractChannel,
):
    await declare_queue(channel)
    await publish(channel, b"event")

    await (await receive(channel, QUEUE)).reject()

    assert (await receive(channel, DEAD_LETTER_QUEUE)).body == b"event"


async def test_declaring_again_keeps_the_messages_of_the_queue(channel: AbstractChannel):
    await declare_queue(channel)
    await publish(channel, b"event")

    await declare_queue(channel)

    assert (await receive(channel, QUEUE)).body == b"event"
