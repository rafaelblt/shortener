---
status: open
resolution:
labels: [question, use_cases, adapters, infra]
---

# 0010: Failures of the infrastructure aren't told apart from bugs

Opened on 2026-10-10.

The use cases don't catch the exceptions raised by the implementations of their abstractions (`docs/use_cases.md`, in Errors of the abstractions). A failure of the infrastructure, such as the database being down or a timeout, reaches the caller of the use case as whatever exception the implementation raised, the same way a bug does. The adapter can only tell them apart by importing the exceptions of each library, such as those of SQLAlchemy.

Whether to tell them apart is still to be decided, before the v1: answering 503 when the infrastructure is unavailable, and 500 for a bug. One way, from the planning of the use cases: a single `InfrastructureError` in `use_cases`, which the implementations in `infra` raise with `raise ... from`, so the adapter doesn't import anything from SQLAlchemy.
