# API

The API is the entry point to the service: it receives HTTP requests and answers them by running the [use cases](use_cases.md). It lives in `shortener/api/`, is built with FastAPI, and imports only from the use cases, the [domain](domain.md) and [`shortener/shared/`](shared.md). What it needs from outside, such as verifying access tokens, it defines as abstractions, which [`infra`](infra.md) implements and [`bootstrap`](bootstrap.md) gives to it.

This document describes the API as it is in the code. Verified bugs that aren't fixed yet are [issues](issues/README.md) labeled `api`, linked from where this document describes the code they affect. Decisions still to be made are in [Open questions](#open-questions).

## Open questions

Decisions to make during this phase. There are none at the moment.
