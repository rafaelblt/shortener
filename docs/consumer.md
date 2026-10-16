# Consumer

The consumer is the entry point of the events the service receives through RabbitMQ: it consumes their messages and handles each one by running a [use case](use_cases.md). It lives in `shortener/consumer/`, is built with [aio-pika](https://aio-pika.readthedocs.io/), and imports only from the use cases, the [domain](domain.md) and [`shortener/shared/`](shared.md). [`bootstrap`](bootstrap.md) connects to RabbitMQ, builds the use case, and runs the consumer as a process of its own, apart from the API.

The only event is the deletion of a user, after which the short URLs of the user are deleted (see [Owner](domain.md#owner)). Its issuer is another system, responsible for the identities of the users, which follows the contract below.

This document describes the consumer as it is in the code. Verified bugs that aren't fixed yet are [issues](issues/README.md) labeled `consumer`, linked from where this document describes the code they affect. Decisions still to be made are in [Open questions](#open-questions).

## Overview

```
shortener/consumer/
├── consumer.py                consume() and PREFETCH_COUNT
├── topology.py                declare_queue(), EXCHANGE, ROUTING_KEY, QUEUE and DEAD_LETTER_QUEUE
├── user_deleted_handler.py    UserDeletedHandler and RETRY_DELAY
└── user_deleted_message.py    parse_user_id()
```

## The event

`user_deleted_message.py`

The issuer publishes the deletion of a user as a persistent message to the exchange `users`, with the routing key `user.deleted`. Its body is a JSON object with the UUID of the user as a string in `user_id`, and its content type is `application/json`:

```json
{"user_id": "0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10"}
```

`parse_user_id(body)` returns the `UUID` of `user_id`, or `None` when the body isn't the one of the event: it isn't JSON, or isn't text, it isn't a JSON object, or its `user_id` is missing, isn't a string, or isn't a UUID.

- The other fields of the object are ignored, so the issuer can add fields without breaking the consumer.
- The content type and the other properties of the message aren't checked: only the body is.
- A UUID is read with `UUID()`, so the forms it takes are accepted too, such as one without hyphens or in braces.

## Topology

`topology.py`

`declare_queue(channel)` declares, on the channel:

| Name                                               | What                                                                                   |
| -------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `EXCHANGE`, `users`                                | The exchange of the events of the users, durable, of the type `topic`                  |
| `QUEUE`, `shortener.user-deleted`                  | The queue of the service, durable, bound to `users` with `ROUTING_KEY`, `user.deleted` |
| `DEAD_LETTER_QUEUE`, `shortener.user-deleted.dead` | The dead-letter queue of `QUEUE`, durable                                              |

It returns `QUEUE`.

- `QUEUE` receives only the messages of `users` whose routing key is `user.deleted`. Another service that needs the same events binds a queue of its own to `users`, and receives a copy of each message.
- A message rejected from `QUEUE` without being requeued goes to `DEAD_LETTER_QUEUE`, through the default exchange, which routes by the name of the queue. It stays there until someone reads it: nothing consumes it.
- The service declares the exchange too, and not only its queues, so it can start before the issuer exists or has declared it.
- Declaring what already exists, with the same arguments, changes nothing, and keeps the messages of the queues. Declaring it with other arguments, such as an exchange `users` of another type, makes RabbitMQ close the channel with an error.

## Handling

`user_deleted_handler.py`

`UserDeletedHandler(delete_shorturls_of_user, retry_delay=RETRY_DELAY)` handles each message of `QUEUE` with [`DeleteShortURLsOfUser`](use_cases.md#deleteshorturlsofuser). `RETRY_DELAY` is 5 seconds.

`handle(message)` takes the user of the message with `parse_user_id()`, and then:

| When                                                                   | It                                                                                                                          |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| The body isn't the one of the event                                    | Logs a warning, and rejects the message without requeuing it, so it goes to the dead-letter queue. The use case doesn't run |
| `execute()` of the use case returns                                    | Acknowledges the message                                                                                                    |
| `execute()` raises [`UnavailableError`](use_cases.md#unavailableerror) | Logs a warning, with the exception, waits `retry_delay`, and then requeues the message                                      |
| `execute()` raises any other exception                                 | Logs it as an error, and rejects the message without requeuing it                                                           |

- The message is acknowledged only after the deletion is committed. A message whose handling stops before that, such as when the process stops or the connection is lost, goes back to the queue and is delivered again. The use case does the same when it runs again for the same user, so a message delivered more than once does no harm.
- A requeued message goes back to its place in the queue, and is delivered again, to this consumer or another one. Without the wait, it would be tried as fast as it fails while the database is unavailable. It is tried again with no limit, until the deletion succeeds.
- Any other exception is a bug, or a failure that trying again won't fix, so the message goes to the dead-letter queue, where it can be read and published again once the cause is fixed. Raised, the message would stay unacknowledged, and the consumer would get no other message until the channel closed.
- The logs name the user, but not the body of a message that isn't the event.

## Consuming

`consumer.py`

`consume(connection, handler)` opens a channel on the connection, limits it to `PREFETCH_COUNT` (1) unacknowledged messages, declares the queues with `declare_queue()`, and starts consuming `QUEUE` with `handler.handle()`. It returns once consuming has started: the messages are handled in the tasks of the connection, one at a time, until the connection is closed.

With one unacknowledged message at a time, the consumer holds only the message it is handling, also while it waits to requeue one, and the others stay in the queue, free for another consumer.

With the robust connection that [`bootstrap`](bootstrap.md#the-consumer) gives it, aio-pika connects again when the connection is lost, and opens the channel, declares the queues and consumes again.

## Open questions

Decisions to make during this phase. There are none at the moment.
