---
status: open
resolution:
labels: [question, use_cases, infra]
---

# 0018: A commit whose result is unknown is answered as unavailable

Opened on 2026-10-13.

When the connection is lost during `commit()`, after Postgres committed the transaction and before its answer arrives, the service can't know whether the transaction was committed. `unavailable_when_transient()` (`shortener/infra/db/transient_errors.py`) raises `UnavailableError` from the lost connection, as for any other one (see `docs/infra.md#failures-of-the-database`), and the API answers `503`, which tells the client to try again. When the transaction was committed, trying again runs the use case a second time:

| Use case                                               | Trying again                                                                  |
| ------------------------------------------------------ | ----------------------------------------------------------------------------- |
| `ResolveSlug`                                          | Counts the resolution twice                                                   |
| `CreateShortURL`, with a generated slug                | Creates a second short URL                                                    |
| `CreateShortURL`, with a given slug                    | Answers `slug_taken`, for the slug of the short URL the first attempt created |
| `DeleteShortURL`                                       | Answers `shorturl_not_found`                                                  |
| `UpdateShortURL`, `EnableShortURL`, `DisableShortURL`  | Changes nothing more                                                          |

Found while restructuring the outer layers. The window is short, between the commit on the server and its answer, and a known solution, such as an idempotency key that the client sends with each request and whose result the service keeps, takes more work than the problem is worth for now. It is recorded so that it isn't forgotten. Whether and how to handle it is still to be decided.
