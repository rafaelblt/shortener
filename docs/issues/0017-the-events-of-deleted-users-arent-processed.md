---
status: closed
resolution: fixed
labels: [todo, use_cases, infra, consumer, bootstrap]
---

# 0017: The events of deleted users aren't processed

Opened on 2026-10-13.

The README (Owner) and `docs/domain.md#owner` say that, when a user is deleted, an external event will trigger the deletion of their short URLs. Nothing does it yet: no use case deletes the short URLs of an owner, `ShortURLRepository` has no method that does it, and nothing receives the events. Until then, the short URLs of a deleted user keep working forever, and not only for the window `docs/domain.md#owner` accepts. Left out of the scope of the restructuring of the outer layers.

How the events arrive, such as a message broker or an endpoint the issuer of the tokens calls, and so which layers receive them, are still to be decided.

## 2026-10-16: Decided on RabbitMQ

The events arrive through RabbitMQ. Their issuer doesn't exist yet: it will be another system, responsible for the identities of the users, so the contract of the event is defined here, and that system follows it.

- **The event:** a persistent message published to the exchange `users`, of the type `topic` and durable, with the routing key `user.deleted`. Its body is JSON, `{"user_id": "<UUID>"}`, with the content type `application/json`.
- **The queue:** the service consumes from a queue of its own, `shortener.user-deleted`, durable and bound to `users` with `user.deleted`, so that other services can receive the same event in queues of their own. A message that can't be processed goes to the dead-letter queue `shortener.user-deleted.dead`. The service declares the exchange, the queues and the binding when it starts, so it doesn't depend on the issuer existing.
- **Processing:** a message is acknowledged only after the deletion is committed, so one whose processing is interrupted is delivered again. Deleting the short URLs of a user is idempotent, so a message delivered more than once does no harm.
  - A message whose body isn't JSON with a UUID in `user_id` is rejected without being requeued, so it goes to the dead-letter queue.
  - When the deletion raises `UnavailableError`, the message is requeued after a pause, so it is tried again without a loop that tries it as fast as it can.
  - Any other exception is a bug, which trying again won't fix: the message is rejected to the dead-letter queue, and the exception is logged.
- **Where:**
  - `use_cases`: a use case that deletes the short URLs of a user, built without `CurrentUser`, since a system asks for it and not the user, and a method of `ShortURLRepository` that deletes them.
  - `infra`: that method with SQLAlchemy.
  - `consumer`: a new layer, `shortener/consumer/`, beside `api/`. It is the entry point of the messages, with aio-pika, and, like `api`, imports the inner layers and not `infra`.
  - `bootstrap`: the URL of RabbitMQ in the settings, and the consumer as a process of its own, apart from the API, with the same image.

A short URL that the user creates after the event is processed, with an access token that is still valid, is issue 0024.

## 2026-10-16: Closed as fixed

The service consumes the events of deleted users from RabbitMQ, as decided above:

- `DeleteShortURLsOfUser` (`shortener/use_cases/delete_shorturls_of_user.py`) deletes every short URL of a user, with the new `remove_by_owner()` of `ShortURLRepository`, which `SQLAlchemyShortURLRepository` implements with a single `DELETE`. See `docs/use_cases.md#deleteshorturlsofuser`.
- The new layer `shortener/consumer/` declares the exchange, the queue and the dead-letter queue, and handles each message with the use case. A message is requeued after `RETRY_DELAY` (5 seconds) when the deletion raises `UnavailableError`, and only one message at a time is unacknowledged. See `docs/consumer.md`.
- `bootstrap` runs the consumer as a process of its own, `python -m shortener.bootstrap.consumer`, with the new `ConsumerSettings`, which read `DATABASE_URL` and `RABBITMQ_URL`. See `docs/bootstrap.md#the-consumer`.
- `compose.yaml` runs RabbitMQ and the consumer, and the `user-deleted` service publishes an event, for local tests.
