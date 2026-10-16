---
status: open
resolution:
labels: [todo, api]
---

# 0020: The OpenAPI schema has no `Location` headers

Opened on 2026-10-16.

Two endpoints answer a `Location` header: `POST /v1/shorturls`, through `Created(location)`, with the path of the new short URL, and `GET /v1/slugs/{slug}/redirect`, through `Redirect(location)`, with the target URL (`docs/api.md#responses`). Neither header is in `docs/openapi.yaml`: the `201` and the `307` of those endpoints have no `headers`, since `add_route()` (`shortener/api/endpoint.py`) gives FastAPI only the status code, the class of response and the model of a `SuccessResponse`. So whoever consumes the API reads in the schema that it creates a short URL or redirects, but not that the response says where.

Whether the schema documents them, and how a `SuccessResponse` would tell `add_route()` which headers it answers, are still to be decided.
