---
status: closed
resolution: fixed
labels: [todo, api]
---

# 0015: Creating a short URL answers no `Location`

Opened on 2026-10-13.

`POST /v1/shorturls` answers `201 Created` with the `ShortURLDetails` (`docs/api.md#endpoints`), through `JSONContent(HTTPStatus.CREATED)`, which sets no header. RFC 9110 (section 15.3.2) says the resource a `201` creates is the one its `Location` header identifies, or, without one, the target URI, which here is `/v1/shorturls` and not the new short URL, `/v1/shorturls/{id}`. Left out of the scope of the restructuring of the outer layers.

Whether to answer `Location`, and how a `SuccessResponse` would build it, are still to be decided.

## 2026-10-16: Decided how the `Location` is answered

`POST /v1/shorturls` answers `Location`, with the path of the new short URL, `/v1/shorturls/{id}`, which `GET /v1/shorturls/{id}` answers. A new `SuccessResponse`, `Created(location)`, builds it from the value of `Ok`, as `Redirect(location)` does.

## 2026-10-16: Closed as fixed

`Created(location)`, in `shortener/api/responses.py`, answers `201 Created` with the value of `Ok` as JSON, serialized with pydantic as FastAPI does, and the URL `location(value)` returns in `Location`. `ENDPOINTS` gives it to `POST /v1/shorturls`, with the `id` of the `ShortURLDetails`. `PREFIX` moved from `app.py` to `shortener/api/prefix.py`, so `endpoints.py` builds the path with it, and the path of a short URL is written once in `endpoints.py`. `docs/api.md` describes it, in Endpoints and Responses.
