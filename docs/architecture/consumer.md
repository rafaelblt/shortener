# Consumer

The consumer is the entry point of the events the service receives through RabbitMQ: it consumes their messages and handles each one by running a [use case](use_cases.md). It lives in `shortener/consumer/`, is built with [aio-pika](https://aio-pika.readthedocs.io/), and imports only from the use cases, the [domain](domain.md) and [`shortener/shared/`](shared.md). [`bootstrap`](bootstrap.md) connects to RabbitMQ, builds the use case, and runs the consumer as a process of its own, apart from the API.

The only event is the deletion of a user, after which the short URLs of the user are deleted (see [Owner](domain.md#owner)). Its contract, and what the service guarantees when it handles it, are in [docs/service/events.md](../service/events.md): this document describes how the code does it.

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

`parse_user_id(body)` returns the `UUID` of `user_id`, or `None` when the body isn't the one of [the message](../service/events.md#the-message): it isn't JSON, or isn't text, it isn't a JSON object, or its `user_id` is missing, isn't a string, or isn't a UUID.

- It only reads `user_id`, and ignores the other fields of the object.
- It receives only the body, so the content type and the other properties of the message aren't checked.
- It reads the UUID with `UUID()`, so the forms it takes are accepted too, such as one without hyphens or in braces.

## Topology

`topology.py`

`declare_queue(channel)` declares, on the channel:

| Name                                               | What                                                                                   |
| -------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `EXCHANGE`, `users`                                | The exchange of the events of the users, durable, of the type `topic`                  |
| `QUEUE`, `shortener.user-deleted`                  | The queue of the service, durable, bound to `users` with `ROUTING_KEY`, `user.deleted` |
| `DEAD_LETTER_QUEUE`, `shortener.user-deleted.dead` | The dead-letter queue of `QUEUE`, durable                                              |

It returns `QUEUE`.

- A message rejected from `QUEUE` without being requeued goes to `DEAD_LETTER_QUEUE`, through the default exchange, which routes by the name of the queue: `QUEUE` has the arguments `x-dead-letter-exchange`, empty, and `x-dead-letter-routing-key`, the name of `DEAD_LETTER_QUEUE`. Nothing consumes it.
- It declares the exchange too, and not only the queues, so the service can start before the publisher exists or has declared it.
- Declaring what already exists, with the same arguments, changes nothing, and keeps the messages of the queues. Declaring it with other arguments, such as an exchange `users` of another type, or `QUEUE` with other arguments, makes RabbitMQ close the channel with an error, so changing what is declared needs what exists to be deleted first.

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

- `execute()` returns once every batch of the deletion is committed, so the message is acknowledged only after every short URL of the user is deleted. What that guarantees, and the rest of what the handling means for the messages, is in [Handling](../service/events.md#handling).
- A requeued message goes back to its place in the queue, and is delivered again, to this consumer or another one. Without the wait, it would be tried as fast as it fails while the database is unavailable.
- Any other exception is a bug, or a failure that trying again won't fix, so the message goes to the dead-letter queue. It is caught, and not raised, since, raised, the message would stay unacknowledged, and the consumer would get no other message until the channel closed.

## Consuming

`consumer.py`

`consume(connection, handler)` opens a channel on the connection, limits it to `PREFETCH_COUNT` (1) unacknowledged messages, declares the queues with `declare_queue()`, and starts consuming `QUEUE` with `handler.handle()`. It returns once consuming has started: the messages are handled in the tasks of the connection, one at a time, until the connection is closed.

With one unacknowledged message at a time, the consumer holds only the message it is handling, also while it waits to requeue one, and the others stay in the queue, free for another consumer.

With the robust connection that [`bootstrap`](bootstrap.md#the-consumer) gives it, aio-pika connects again when the connection is lost, and opens the channel, declares the queues and consumes again.
