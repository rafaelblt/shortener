# Infrastructure

The infrastructure implements the abstractions the other layers define: those of the [use cases](use_cases.md#abstractions), such as storing short URLs, and those of the [API](api.md), such as verifying access tokens. It lives in `shortener/infra/`, and imports only from the use cases, the [domain](domain.md) and [`shortener/shared/`](shared.md). It doesn't read settings or build anything on its own: [`bootstrap`](bootstrap.md) builds its implementations and gives them to the layers that use them.

This document describes the infrastructure as it is in the code. Verified bugs that aren't fixed yet are [issues](issues/README.md) labeled `infra`, linked from where this document describes the code they affect. Decisions still to be made are in [Open questions](#open-questions).

## Open questions

Decisions to make during this phase. There are none at the moment.
