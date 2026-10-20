---
status: open
resolution:
labels: [question, consumer, infra]
---

# 0025: A deletion longer than the statement timeout is retried forever

Opened on 2026-10-16.

`remove_by_owner()` (`shortener/infra/db/shorturl_repository.py`) deletes every short URL of a user in a single `DELETE`, which, like any statement, runs for at most the `DATABASE_STATEMENT_TIMEOUT` of the [settings](../bootstrap.md#settings), 30 seconds by default. For a user with enough short URLs that the `DELETE` takes longer, Postgres cancels it with `57014`, which is [transient](../infra.md#failures-of-the-database), so it is raised as `UnavailableError`. The [handler of the consumer](../consumer.md#handling) then requeues the message after `RETRY_DELAY` (5 seconds), with no limit. The deletion would take as long on every attempt, so the message would be tried again forever, and none of the short URLs of the user would be deleted, since each attempt is rolled back.

This follows from the code, and wasn't reproduced. The `DELETE` uses the index `ix_shorturls_owner_id_created_at_id` to find the rows, so it would take a user with very many short URLs, or a much shorter `DATABASE_STATEMENT_TIMEOUT`.

Whether to handle it, and how, is still to be decided. Some ways:

- Delete the short URLs in batches, each in a transaction of its own, so each statement stays short, and an attempt that fails keeps what the previous batches deleted.
- Give the deletion a longer statement timeout than the one of the API.
- Limit the attempts of a message, such as with the delivery limit of a quorum queue, so that it goes to the dead-letter queue after them.

## 2026-10-20: Reproduced, and the message holds back the ones behind it

Reproduced with `run_consumer()`, the process of the consumer, on Postgres 17 and RabbitMQ 4 in containers, with a `DATABASE_STATEMENT_TIMEOUT` of 200 ms. A user A had 1,000,000 short URLs and a user B had one, and the event of A was published before the one of B. In the 20 seconds watched:

| Consumers | User A                                                                                                                                 | User B                                           |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| 1         | Put back in the queue 4 times, each after `57014` ("canceling statement due to statement timeout"), and none of its short URLs deleted | Never handled, and its short URL kept            |
| 2         | The same                                                                                                                               | Deleted after 0.5 seconds, by the other consumer |

RabbitMQ puts a message rejected with `requeue` back in its original position in a classic queue, which is the head here, so it is delivered again at once, and a consumer, which [handles one message at a time](../architecture/consumer.md#consuming), handles nothing else. So each such message holds back a consumer for good, and with as many of them as there are consumers, no event of a deleted user is handled anymore, until the messages are removed from the queue by hand.
