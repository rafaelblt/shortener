# Events

The events the service receives from other systems, through RabbitMQ, and what it does with them. The consumer of the events runs as a process of its own, apart from the API (see [Running](running.md#the-processes)). How the code does what this document describes is in [the architecture of the consumer](../architecture/consumer.md).

There is one event: the deletion of a user.

## The deletion of a user

When a user is deleted, the system responsible for the identities of the users publishes the event, and the service deletes every short URL of the user. From then on, their slugs are free, and resolving them answers `shorturl_not_found`.

That system doesn't exist yet, so the contract of the event is defined here, for it to follow.

### The message

A persistent message, published to the exchange `users`, of the type `topic` and durable, with the routing key `user.deleted`. Its body is a JSON object with the UUID of the user as a string in `user_id`, and its content type is `application/json`:

```json
{"user_id": "0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10"}
```

- The other fields of the object are ignored, so the publisher can add fields without breaking the service.
- Only the body is checked: the content type and the other properties of the message aren't.
- The forms that Python accepts for a UUID are accepted too, such as one without hyphens or in braces.

### The queues

The service declares, when it starts, the exchange `users` and two queues of its own, all durable:

| Queue                         | What                                                                              |
| ----------------------------- | --------------------------------------------------------------------------------- |
| `shortener.user-deleted`      | The queue of the events the service handles, bound to `users` with `user.deleted` |
| `shortener.user-deleted.dead` | The dead-letter queue, where the messages the service rejects go                  |

- Declaring the exchange too lets the service start before the publisher exists or has declared it. Declaring what already exists, with the same arguments, changes nothing and keeps the messages.
- Another service that needs the same events binds a queue of its own to `users`, and receives a copy of each message.
- Nothing consumes the dead-letter queue: a message stays there until someone reads it, and can be published again once its cause is fixed.

### Handling

| When                                                                                                                   | The service                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| The short URLs are deleted                                                                                             | Acknowledges the message                                                                    |
| The body isn't the one of the event: it isn't JSON, isn't an object, or has no UUID in `user_id`                       | Logs a warning, and rejects the message to the dead-letter queue, without deleting anything |
| The database is unavailable, or a wait on it runs out, such as its statement timeout                                   | Logs a warning, waits 5 seconds, and puts the message back in the queue, to be tried again  |
| Anything else fails, such as a bug, or a failure of the database that trying again won't fix, such as a wrong password | Logs the error, and rejects the message to the dead-letter queue                            |

- The short URLs of the user are deleted in batches of up to 1000, each committed on its own, until none is left, so that each statement of the database deletes few of them, and stays short, whatever the number of short URLs of the user. When the deletion fails, the batches before the failure stay deleted, and the next attempt of the message goes on from there.
- The message is acknowledged only after every short URL of the user is deleted. A message whose handling stops before that, such as when the process stops or the connection is lost, goes back to the queue and is delivered again. Deleting the short URLs of a user twice does the same as once, so a message delivered more than once does no harm.
- A message put back in the queue is tried again with no limit, until the deletion succeeds or fails in another way.
- Each process of the consumer handles one message at a time, also while it waits to put one back, and leaves the others in the queue, free for another process. RabbitMQ delivers each message to only one process.
- The logs name the user, but not the body of a message that isn't the event.

### Known limitations

- Until the message is handled, the short URLs of the user that aren't deleted yet keep resolving. That is accepted, since it doesn't harm the shortener (see [Owner](../architecture/domain.md#owner)).
- A short URL that the user creates after the message is handled, with an access token issued before the deletion, is never deleted ([issue 0024](../issues/0024-a-deleted-user-can-create-short-urls-until-their-token-expires.md)).
- The deletion of a user takes longer the more short URLs they have, and nothing limits how many a user can have. While a process of the consumer deletes them, it handles no other message ([issue 0028](../issues/0028-a-user-can-have-any-number-of-short-urls.md)).
