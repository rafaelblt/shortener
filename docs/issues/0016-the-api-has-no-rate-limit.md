---
status: closed
resolution: fixed
labels: [todo, api]
---

# 0016: The API has no rate limit

Opened on 2026-10-13.

Nothing limits how many requests a client makes, to any endpoint: creating short URLs, or resolving slugs, where each resolution writes to the database. Left out of the scope of the restructuring of the outer layers.

Which endpoints to limit, by what (the user of the token, the IP address), with which limits, and whether in the service or in a proxy in front of it, as with the domain of short links (`docs/api.md#endpoints`), are still to be decided.

## 2026-10-15: Closed as fixed

The service limits the requests of each IP address. What was decided:

- Every endpoint of `ENDPOINTS` is limited, with one count for all of them. The documentation of FastAPI isn't.
- By the IP address of the client, the one the server gives. Behind a proxy, uvicorn takes it from `X-Forwarded-For` when it trusts the proxy (`docs/bootstrap.md#running`).
- 60 requests a minute by default, set with `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW`.
- In the service, with the counts in the memory of the process, so each worker or replica counts apart.

A request over the limit gets `429 Too Many Requests`, with the code `too_many_requests` and the header `Retry-After`. The API counts the requests through the `RateLimiter` abstraction (`shortener/api/rate_limit.py`), which `InMemoryRateLimiter` (`shortener/infra/in_memory_rate_limiter.py`) implements with a fixed window (see `docs/api.md#rate-limit` and `docs/infra.md#rate-limit`).
