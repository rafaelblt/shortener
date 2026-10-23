---
status: open
resolution:
labels: [question, use_cases, consumer]
---

# 0028: A user can have any number of short URLs

Opened on 2026-10-23.

`CreateShortURL` (`shortener/use_cases/create_shorturl.py`) creates a short URL whatever the number of short URLs its owner already has, so nothing limits how many a user can have.

The handling of the [event](../service/events.md#the-deletion-of-a-user) of the deletion of a user deletes all of their short URLs, so the time it takes grows with their number, and has no upper bound. That holds with the deletion in batches accepted in [issue 0025](0025-a-deletion-longer-than-the-statement-timeout-is-retried-forever.md) too: each batch is short, but nothing limits how many batches there are. While it runs, the consumer handles no other message (see [Consuming](../architecture/consumer.md#consuming)), and there is no worst case to size it for, or to test.

Whether to handle it, and how, is still to be decided. The maintainer favors a fixed maximum of short URLs per user, technical and not a rule of the product: wide enough that ordinary use doesn't reach it, and there to bound the work of the deletion of a user. A rule of the product that limits the short URLs of a user, which the service has no plan for now, or one set by whoever runs the service, would be lower, and the maximum would still hold beneath it.

Still to be analyzed: the value of the maximum, how the creation checks it and what that costs, and what the API answers to a user who reached it.
