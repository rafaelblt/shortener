---
status: closed
resolution: fixed
labels: [todo, api]
---

# 0020: The OpenAPI schema has no `Location` headers

Opened on 2026-10-16.

Two endpoints answer a `Location` header: `POST /v1/shorturls`, through `Created(location)`, with the path of the new short URL, and `GET /v1/slugs/{slug}/redirect`, through `Redirect(location)`, with the target URL (`docs/api.md#responses`). Neither header is in `docs/openapi.yaml`: the `201` and the `307` of those endpoints have no `headers`, since `add_route()` (`shortener/api/endpoint.py`) gives FastAPI only the status code, the class of response and the model of a `SuccessResponse`. So whoever consumes the API reads in the schema that it creates a short URL or redirects, but not that the response says where.

Whether the schema documents them, and how a `SuccessResponse` would tell `add_route()` which headers it answers, are still to be decided.

## 2026-10-16: Closed as fixed

The schema documents them. A `SuccessResponse` describes the headers it answers in `header_descriptions`, with the description of each one: `Created` and `Redirect` describe their `Location`, and `JSONContent` and `NoContent` describe none. `add_route()` gives them to FastAPI as the headers of the response of success, through `documented_headers()`, in the new `shortener/api/openapi.py`. So the `201` of `POST /v1/shorturls` and the `307` of `GET /v1/slugs/{slug}/redirect` have `Location` in `docs/openapi.yaml`, and `docs/api.md` describes it, in OpenAPI, How an endpoint works and Responses.
