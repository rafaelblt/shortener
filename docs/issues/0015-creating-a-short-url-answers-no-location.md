---
status: open
resolution:
labels: [todo, api]
---

# 0015: Creating a short URL answers no `Location`

Opened on 2026-10-13.

`POST /v1/shorturls` answers `201 Created` with the `ShortURLDetails` (`docs/api.md#endpoints`), through `JSONContent(HTTPStatus.CREATED)`, which sets no header. RFC 9110 (section 15.3.2) says the resource a `201` creates is the one its `Location` header identifies, or, without one, the target URI, which here is `/v1/shorturls` and not the new short URL, `/v1/shorturls/{id}`. Left out of the scope of the restructuring of the outer layers.

Whether to answer `Location`, and how a `SuccessResponse` would build it, are still to be decided.
