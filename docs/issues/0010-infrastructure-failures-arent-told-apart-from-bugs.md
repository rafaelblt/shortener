---
status: open
resolution:
labels: [question, use_cases, adapters, infra]
---

# 0010: Failures of the infrastructure aren't told apart from bugs

Opened on 2026-10-10.

The use cases don't catch the exceptions raised by the implementations of their abstractions (`docs/use_cases.md`, in Errors of the abstractions). A failure of the infrastructure, such as the database being down or a timeout, reaches the caller of the use case as whatever exception the implementation raised, the same way a bug does. The adapter can only tell them apart by importing the exceptions of each library, such as those of SQLAlchemy.

Whether to tell them apart is still to be decided, before the v1: answering 503 when the infrastructure is unavailable, and 500 for a bug. One way, from the planning of the use cases: a single `InfrastructureError` in `use_cases`, which the implementations in `infra` raise with `raise ... from`, so the adapter doesn't import anything from SQLAlchemy.

## 2026-10-11: Decided on a single `UnavailableError`

They will be told apart, by a single exception, `UnavailableError`, in `use_cases`, instead of the `InfrastructureError` above. The name says what the adapter needs to know, while `InfrastructureError` suggests any exception raised in `infra`.

- **What it means:** an implementation of an abstraction couldn't do what it was asked now, for a reason that is expected to go away, so trying the operation again may succeed. For example, the database is down, a timeout, no free connection in the pool, or a wait for a lock that ran out. The implementations raise it with `raise UnavailableError() from error`, so the exception of the library stays in `__cause__`, for the logs.
- **What it doesn't cover:** a failure that trying again won't fix, such as a bug in a mapper or a table that doesn't exist, isn't wrapped, and still reaches the adapter as it is. Neither is a failure that isn't known to go away. Wrapping a bug would answer 503 to it: the client would keep trying again, and nothing would flag the bug. The class of the exception isn't always enough to decide: on SQLite, `no such table` and `database is locked` are both an `OperationalError`.
- **No subclasses and no fields:** the adapter answers the same to every one of them, whatever failed, so a subclass per component, such as the database, wouldn't change the response. What failed is in `__cause__`, and doesn't go in the response. A subclass can be added later, when something has to react to one case differently, and `except UnavailableError` still catches it.
- **An exception, not an `Err`:** no use case handles it, so it goes through them, and through `async with uow.begin()`, which rolls the transaction back. The use cases don't change.
- **In the adapter:** 503 Service Unavailable for `UnavailableError`, and 500 for any other exception. Not 502 or 504, which are for a server acting as a gateway or a proxy.

Still to do: `UnavailableError`, and its place in the contract of the abstractions, in `shortener/use_cases/` and `docs/use_cases.md`; raising it in the implementations, in the phase of `infra`; and answering 503 to it, in the phase of `adapters`.
