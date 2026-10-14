---
status: open
resolution:
labels: [bug, infra]
---

# 0012: A connection lost in a transaction can be raised as an `InternalClientError` of asyncpg

Opened on 2026-10-11.

When Postgres ends the session of a transaction that is still open, such as when the server restarts or an administrator ends it, the next statement of the transaction, or its `commit()`, fails. SQLAlchemy usually raises it as a `DBAPIError` whose `connection_invalidated` is true, which `is_transient()` (`shortener/infra/db/transient_errors.py`) takes as transient, so `unavailable_when_transient()` raises `UnavailableError` from it. But when asyncpg has received the message of the server that ends the session, and hasn't noticed yet that the connection was closed, it raises `asyncpg.exceptions._base.InternalClientError` (`cannot switch to state 15; another operation (2) is in progress`). SQLAlchemy doesn't wrap it, it has no SQLSTATE, and it goes through as it is.

To reproduce: begin a transaction with `SQLAlchemyUnitOfWork`, read a short URL through it, end its session from another connection with `pg_terminate_backend()`, and call `commit()` right away. In 5 attempts, 3 raised `InternalClientError` and 2 `UnavailableError`. Waiting 50 milliseconds before `commit()` raised `UnavailableError` in every attempt.

Expected, from `docs/use_cases.md` (UnavailableError): a lost connection is a failure that trying again may fix, which the implementations raise as `UnavailableError`. With `InternalClientError`, the caller gets the error of a bug. How to tell this `InternalClientError` apart from one that isn't a lost connection is still to be decided.

## 2026-10-13: Decided to take every `InternalClientError` as transient

It can't be told apart by its type, which is the same for every broken state of the protocol of asyncpg, and not by whether the connection is closed, since asyncpg hasn't noticed it yet when it raises it. Matching its message would break with a new version of asyncpg. So `is_transient()` takes every `InternalClientError` as transient. No code of the project raises it, and the connection can't be used after it either way. The cost is that a bug of asyncpg is answered with `503` instead of `500`, still logged with its cause.
