# Bootstrap

`bootstrap` assembles the application: it reads the settings, builds the implementations of [`infra`](infra.md), builds the [use cases](use_cases.md) with them, and gives them to the [API](api.md). It lives in `shortener/bootstrap/`, and is the only layer that imports from every other one.

This document describes `bootstrap` as it is in the code. Verified bugs that aren't fixed yet are [issues](issues/README.md) labeled `bootstrap`, linked from where this document describes the code they affect. Decisions still to be made are in [Open questions](#open-questions).

## Open questions

Decisions to make during this phase. There are none at the moment.
