---
status: closed
resolution: fixed
labels: [todo, use_cases, consumer, infra]
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

## 2026-10-23: Accepted: deleting in batches

Of the ways above, the maintainer accepted the first one: the short URLs of the user are deleted in batches, each in a transaction of its own, until none is left. Each statement deletes few enough rows to stay under the statement timeout, and an attempt that fails keeps what the batches before it deleted, so the next attempt of the message goes on from there, instead of starting over.

It isn't implemented yet.

How long the deletion takes still grows with the short URLs of the user, which nothing limits: that is [issue 0028](0028-a-user-can-have-any-number-of-short-urls.md).

## 2026-10-23: Closed as fixed

`DeleteShortURLsOfUser` (`shortener/use_cases/delete_shorturls_of_user.py`) deletes the short URLs of the user in batches of up to `BATCH_SIZE` (1000), each in a transaction of its own, which it commits, until a batch deletes none. `remove_by_owner()` receives the most short URLs it deletes, `limit`, and returns how many it deleted. `SQLAlchemyShortURLRepository` deletes the rows of the owner that a subquery with `LIMIT` and `FOR UPDATE` picks, so a row that another transaction removes while the batch waits for it is replaced by another one of the owner, and it returns `0` only when the owner has none left. An attempt that fails keeps the batches committed before it, and the next attempt of the message goes on from there. `docs/architecture/use_cases.md`, in DeleteShortURLsOfUser, and `docs/service/events.md`, in Handling, describe it.

The reproduction above, run again with one consumer and the deletion in batches: the 1,000,000 short URLs of user A were deleted in about 9 seconds, with no message put back in the queue, and the short URL of user B right after them. A batch of 1000 took about 10 ms in a table of 2,000,000 short URLs, a tenth of them of the user, and from 25 to 50 ms in one of 5,000,000, a hundredth of them of the user, with the last batches as fast as the first ones.
