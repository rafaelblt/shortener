---
status: open
resolution:
labels: [todo, docs, consumer]
---

# 0026: The documents don't say a message retried forever holds back the others

Opened on 2026-10-20.

[Issue 0025](0025-a-deletion-longer-than-the-statement-timeout-is-retried-forever.md#2026-10-20-reproduced-and-the-message-holds-back-the-ones-behind-it) reproduced that a message whose deletion always fails with a transient error is delivered again at once to the consumer that put it back in the queue, since RabbitMQ puts it back at its place, the head, and that consumer handles nothing else from then on. With one process of the consumer, the events of the other deleted users behind it are never handled.

The documents don't say it, and two of their sentences suggest otherwise:

- [Known limitations](../service/events.md#known-limitations), in `docs/service/events.md`, says only that the deletion of that user fails every time and that its message is tried again forever.
- [Handling](../service/events.md#handling), in the same document, says that each process "leaves the others in the queue, free for another process", and [Consuming](../architecture/consumer.md#consuming), in `docs/architecture/consumer.md`, that "the others stay in the queue, free for another consumer". That holds while the message is handled, but not after it is put back: with a single process, there is no other one to take them.
- [Handling](../architecture/consumer.md#handling), in `docs/architecture/consumer.md`, says that a requeued message "is delivered again, to this consumer or another one", without saying that it comes back ahead of the messages behind it.

The documents would describe that a message that always fails with a transient error holds back one process of the consumer for good, and that with as many such messages as processes, no event of a deleted user is handled until they are removed from the queue by hand.
