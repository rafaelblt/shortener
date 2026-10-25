---
status: open
resolution:
labels: [bug, api]
---

# 0029: The API reads a body of any size, and one that isn't JSON skips the rate limit

Opened on 2026-10-24.

Nothing limits the size of the body of a request. FastAPI reads the whole body of `POST /api/v1/shorturls` and `PATCH /api/v1/shorturls/{id}` into memory, and parses it, before it runs the dependencies of the route, so before the [rate limit](../service/api.md#rate-limit), which is a dependency of the router (`shortener/api/rate_limit.py`), and before the access token. Neither uvicorn nor FastAPI limits the size of a body by default.

A body that isn't valid JSON is answered `400` with `malformed_body` before the rate limit, so it never counts, as the [rate limit](../service/api.md#rate-limit) says. So a client, without an access token, can make the API read bodies of any size, as many as it sends, and never gets `429`. A body that is valid JSON counts, but is read and parsed in full before it is counted.

To reproduce, with `create_app()` (`shortener/api/app.py`) built with a `RateLimiter` that counts its calls: 10 requests `POST /api/v1/shorturls` with a body of 20 MB that isn't JSON are all answered `400`, and `hit()` is never called.

[Behind a proxy](../service/running.md#behind-a-proxy) doesn't mention the size of the bodies either. Whether to limit it, with which maximum, and whether in the service or in a proxy in front of it, is still to be decided. See also [issue 0030](0030-a-target-url-has-no-maximum-length.md), on the length of a target URL.
