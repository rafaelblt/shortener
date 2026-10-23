---
status: closed
resolution: fixed
labels: [todo, docs]
---

# 0026: The documents don't say that a requeued message holds back the ones behind it

Opened on 2026-10-20.

When the deletion of a user fails with a transient error, the consumer waits and puts the message back in the queue. RabbitMQ puts it back at its place, the head of the queue, so it is delivered again at once, often to the same consumer, which handles one message at a time. A message whose deletion fails every time, as in [issue 0025](0025-a-deletion-longer-than-the-statement-timeout-is-retried-forever.md), where this was reproduced, holds back that consumer for good, and with as many such messages as there are consumers, no event of a deleted user is handled anymore.

The documents don't say so:

- [Known limitations](../service/events.md#known-limitations) in `docs/service/events.md` says that the deletion of such a user is tried again forever, and not that the events of the other users behind it wait too.
- [Handling](../service/events.md#handling) in `docs/service/events.md` says that each process "leaves the others in the queue, free for another process", and [Consuming](../architecture/consumer.md#consuming) in `docs/architecture/consumer.md` says the same of a consumer. That holds only when there is another process, and while the one that put the message back doesn't get it again.
- [Handling](../architecture/consumer.md#handling) in `docs/architecture/consumer.md` says that a requeued message goes back to its place in the queue, and is delivered again, "to this consumer or another one", without what that does to the messages behind it.

## 2026-10-23: Closed as fixed

The documents say it now:

- `docs/service/events.md`, in Handling, says that a message put back in the queue goes back to its place, ahead of the messages that arrived after it, and is delivered again before them, often to the same process, and that each process leaves the others free for another process only if there is one. In Known limitations, it says that such a message holds back the process that gets it again for as long as its deletion keeps failing, that the messages behind it wait for another process, and that, with as many such messages as processes, no message is handled.
- `docs/architecture/consumer.md`, in Handling and in Consuming, says the same of a consumer, and links to the service.

The bullet of Known limitations that said that the deletion of a user with too many short URLs was tried again forever went away with the fix of [issue 0025](0025-a-deletion-longer-than-the-statement-timeout-is-retried-forever.md), whose deletion in batches no longer fails for that.
