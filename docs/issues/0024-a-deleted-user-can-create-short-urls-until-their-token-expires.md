---
status: open
resolution:
labels: [question, domain, use_cases]
---

# 0024: A deleted user can create short URLs until their token expires

Opened on 2026-10-16.

`docs/domain.md#owner` accepts that the short URLs of a deleted user keep working until the event of the deletion is processed, which is issue 0017. That window doesn't cover what happens after it: the service verifies an access token by itself, and doesn't know which users were deleted (`docs/infra.md#access-tokens`), so a token issued to the user before the deletion stays valid until its `exp`. If the user creates a short URL with it after the event was processed, the event doesn't come again, and that short URL is never deleted.

Whether to handle it, and how, is still to be decided. Some ways, from the discussion of issue 0017:

- Accept it, if the tokens are short-lived.
- Keep the IDs of the deleted users, and refuse to create short URLs for them.
- Delete the short URLs of the user again after their tokens can no longer be valid.

## 2026-10-20: Favoring a maximum lifetime of the tokens and a second deletion

Of the ways above, the maintainer favors, for now, the last one, with the service bounding the lifetime of the tokens by itself, instead of relying on the issuer:

- A new setting, such as `JWT_MAX_LIFETIME`: an access token whose `exp` is further from now than it isn't valid. It needs no `iat`, which a token may not have.
- When the consumer handles the [event](../service/events.md#the-deletion-of-a-user) of a deletion, it deletes the short URLs of the user, as it does now, and schedules a second deletion for after `JWT_MAX_LIFETIME` plus `JWT_LEEWAY`, when no token issued before the deletion can still be valid. In RabbitMQ, for example, with a queue whose messages expire after that time and are dead-lettered back to `shortener.user-deleted`, marked so that the second deletion doesn't schedule a third.

Why it is favored over the other two:

- Short-lived tokens alone make the window smaller, but a short URL created in it is still never deleted.
- Keeping the IDs of the deleted users makes the service decide whether a user may act, which is the role of the system of the identities of the users, and keeps a state about users that the service doesn't have.
- The second deletion turns "never deleted" into a bounded window, like the one [Owner](../architecture/domain.md#owner) already accepts until the event is processed. It uses the same deletion, which is idempotent, keeps no state about users, and doesn't change the API.

Still to be decided: the value of `JWT_MAX_LIFETIME`, and whether it has a default.
