# API

The API is the entry point to the service: it receives HTTP requests and answers them by running the [use cases](use_cases.md). It lives in `shortener/api/`, is built with FastAPI, and imports only from the use cases, the [domain](domain.md) and [`shortener/shared/`](shared.md). What it needs from outside, such as verifying access tokens, it defines as abstractions, which [`infra`](infra.md) implements and [`bootstrap`](bootstrap.md) gives to it.

This document describes the API as it is in the code. Verified bugs that aren't fixed yet are [issues](issues/README.md) labeled `api`, linked from where this document describes the code they affect. Decisions still to be made are in [Open questions](#open-questions).

## Overview

```
shortener/api/
├── app.py                     create_app()
├── prefix.py                  PREFIX
├── endpoints.py               ENDPOINTS
├── endpoint.py                Endpoint, add_route() and PARAMETER_TYPES
├── responses.py               SuccessResponse, JSONContent, Created, NoContent and Redirect
├── errors.py                  ERRORS, ErrorResponse, ErrorContent, error_response() and the
│                              handlers of exceptions
├── authentication.py          AccessTokenVerifier and AccessTokenCurrentUser
├── rate_limit.py              RateLimiter, TooManyRequestsError and limit_by_ip()
├── health_check.py            HealthCheck and add_health_check_route()
├── use_case_factory.py        UseCaseFactory
├── cursors.py                 encode_cursor(), decode_cursor() and CursorParameter
└── shorturl_page_content.py   ShortURLPageContent
```

The API defines four abstractions, as `Protocol`s, which it receives in `create_app()`:

| Abstraction                              | What it does                                                                 | Implementation                                                 |
| ---------------------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------- |
| [`UseCaseFactory`](#use-cases)           | Builds the use case of a request, with the user making it                    | [`UseCases`](bootstrap.md#use-cases), in `bootstrap`           |
| [`AccessTokenVerifier`](#authentication) | Tells whose an access token is                                               | [`JWTAccessTokenVerifier`](infra.md#access-tokens), in `infra` |
| [`RateLimiter`](#rate-limit)             | Counts the requests of each IP address, and tells when one is over its limit | [`InMemoryRateLimiter`](infra.md#rate-limit), in `infra`       |
| [`HealthCheck`](#health-check)           | Tells whether the service is able to answer                                  | [`SQLAlchemyHealthCheck`](infra.md#health-check), in `infra`   |

## The application

`app.py`

`create_app(use_cases, access_token_verifier, rate_limiter, health_check, endpoints=ENDPOINTS, lifespan=None)` returns the FastAPI application. It adds a route for each [endpoint](#endpoints), and the one of the [health check](#health-check), under `PREFIX` (`/v1`), with the [rate limit](#rate-limit) of `rate_limiter` on the endpoints, and the handlers of the exceptions that become [errors](#errors). `lifespan` is the one of FastAPI, for what has to run when the application starts and stops. It raises `LookupError` when the use case of an endpoint may return an error the API doesn't answer (see [How an endpoint works](#how-an-endpoint-works)), so the application doesn't start.

## OpenAPI

The API doesn't serve its OpenAPI schema, nor the documentation of FastAPI: `/openapi.json`, `/docs` and `/redoc` answer `not_found`, like any path that no endpoint has. The schema is in [openapi.yaml](openapi.yaml), which `poetry run task openapi` writes from what `create_app()` gives, and a test of `tests/test_api/test_app.py` fails when the file isn't the schema of the code. So a change to what the API receives or answers, such as an endpoint, a parameter or an error, comes with the file written again.

Whoever consumes the API reads the schema where its code is, without running the API, opens it in any tool that previews OpenAPI or gives it to an agent, and sees its changes in the diff. And the API running in production doesn't expose it.

## Endpoints

`endpoints.py`

`ENDPOINTS` declares each endpoint of the API, with the use case it runs:

| Method and path                   | Use case                                                             | Receives                                                | Answers                                                    |
| --------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------- | ---------------------------------------------------------- |
| `GET /v1/slugs/{slug}`            | [`ResolveSlug`](use_cases.md#resolveslug)                            | `slug`, in the path                                     | `200 OK`, with the `ResolvedSlug`: `{"target_url": "..."}` |
| `GET /v1/slugs/{slug}/redirect`   | [`ResolveSlug`](use_cases.md#resolveslug), named `RedirectSlug`      | `slug`, in the path                                     | `307 Temporary Redirect` to the target URL                 |
| `POST /v1/shorturls`              | [`CreateShortURL`](use_cases.md#createshorturl)                      | `target_url` and `slug`, in the body                    | `201 Created`, with the `ShortURLDetails` and `Location`   |
| `GET /v1/shorturls`               | [`ListShortURLs`](use_cases.md#listshorturls)                        | `limit` and `cursor`, in the query                      | `200 OK`, with a [`ShortURLPageContent`](#cursors)         |
| `GET /v1/shorturls/{id}`          | [`GetShortURL`](use_cases.md#getshorturl)                            | `id`, in the path                                       | `200 OK`, with the `ShortURLDetails`                       |
| `PATCH /v1/shorturls/{id}`        | [`UpdateShortURL`](use_cases.md#updateshorturl)                      | `id`, in the path, `target_url` and `slug`, in the body | `200 OK`, with the `ShortURLDetails`                       |
| `POST /v1/shorturls/{id}/enable`  | [`EnableShortURL`](use_cases.md#enableshorturl-and-disableshorturl)  | `id`, in the path                                       | `200 OK`, with the `ShortURLDetails`                       |
| `POST /v1/shorturls/{id}/disable` | [`DisableShortURL`](use_cases.md#enableshorturl-and-disableshorturl) | `id`, in the path                                       | `200 OK`, with the `ShortURLDetails`                       |
| `DELETE /v1/shorturls/{id}`       | [`DeleteShortURL`](use_cases.md#deleteshorturl)                      | `id`, in the path                                       | `204 No Content`                                           |

What each one receives and answers follows from its use case, by the rules of [How an endpoint works](#how-an-endpoint-works):

- The two endpoints of a slug run `ResolveSlug`, so both count the resolution. `GET /v1/slugs/{slug}` answers the target URL, for a system that uses the shortener and decides what to do with it, such as showing a page before it redirects. `GET /v1/slugs/{slug}/redirect` redirects to it, for a system that wants the redirect done. The shortener is meant to serve other systems without imposing how they resolve a slug, so it has both.
- Every endpoint but the two of a slug reads the [access token](#authentication), since its use case takes a `CurrentUser`.
- `slug`, and the `target_url` of a `PATCH`, default to `None` in `execute()`, so a `null` is the same as leaving them out: `POST /v1/shorturls` generates the slug, and `PATCH /v1/shorturls/{id}` doesn't change them. A `PATCH` with no value to change gets `nothing_to_update`. The `target_url` of a `POST` has no default, so leaving it out, or sending it as `null`, gets `missing`.
- `limit` is 20 when the query leaves it out, the default of `ListShortURLs.execute()`.
- The `Location` of `POST /v1/shorturls` is the path of the new short URL, `/v1/shorturls/{id}`, with the `id` of its `ShortURLDetails`, which `GET /v1/shorturls/{id}` answers.
- The redirect is temporary, so the clients don't keep it: each visit asks the service again, which counts the resolution, and follows changes of the target URL and deactivations.
- Every route is under `/v1`, so a slug never shares a path with a route of the API, and no slug has to be reserved. A domain of short links, where `/{slug}` redirects, is a proxy in front of the service, which sends `/{slug}` to `/v1/slugs/{slug}/redirect`. The rules of [`Slug.create()`](domain.md#slug) don't allow dots, so a path such as `/favicon.ico` is never the slug of a new short URL.
- The JSON of a `ShortURLDetails` has its fields, with the IDs as text, and the datetimes in ISO 8601, with `Z` for UTC.
- The OpenAPI schema groups the two endpoints of a slug in the tag `Slugs`, and the others in `Short URLs`.

## How an endpoint works

`endpoint.py`

`Endpoint(method, path, use_case, response=JSONContent(), *, summary, tag, name=None)` declares an endpoint, and `add_route()` adds it to the router of FastAPI. Only the method, the path, the use case, how to answer its `Ok`, a summary and a tag are declared, and, when it needs one, a name: what the endpoint receives, who makes the request and how errors are answered come from the use case.

**Parameters.** Each parameter of `execute()` becomes one of the request, with its name, its type and its default:

- When its name is in the path, such as `{id}`, it comes from the path.
- Otherwise, it comes from the query when the method is `GET` or `DELETE`, and from a field of the JSON object of the body for the other methods.
- It is required when `execute()` has no default for it, and a `null` for it in the body is the same as leaving it out. Otherwise, a request that leaves it out gives the default of `execute()`.
- FastAPI reads it as the type of `execute()`, such as a `UUID` from the text of the path, or an `int` from the text of the query. A type that is in `PARAMETER_TYPES` is read as the type it maps to instead, which is how a request carries a [`ShortURLCursor`](#cursors). In a union, such as `ShortURLCursor | None`, each member is replaced.

Since the name of a parameter of `execute()` is the name of its value in the request, the `field` of a [`FieldError`](use_cases.md#errors-of-the-use-cases) of the use case is the name the client sent.

**Access token.** When the constructor of the use case takes a `CurrentUser`, the endpoint reads the `Authorization` header, with the `Bearer` scheme, and the OpenAPI schema says the endpoint takes a bearer token. Otherwise, it doesn't read the header.

**Running.** For each request, the endpoint:

1. builds an [`AccessTokenCurrentUser`](#authentication) with the token, or with `None` when the header is missing, isn't of the `Bearer` scheme, or isn't read;
2. asks the [`UseCaseFactory`](#use-cases) for the use case, with that current user;
3. awaits `execute()`, with the values of the request as keyword arguments;
4. answers `Ok` with its [`SuccessResponse`](#responses), and `Err` with [`error_response()`](#errors).

FastAPI reads the values of the request before step 1, so a request whose values it can't read gets an [error](#errors) without the use case being built. It runs the [rate limit](#rate-limit) after parsing the JSON of the body and before reading the values, so a request over the limit gets `too_many_requests` even when its values can't be read.

**OpenAPI.** The name of the endpoint is its name and operation ID, and is the name of its use case when `name` is `None`. Two endpoints of the same use case need different names, since FastAPI warns about a repeated operation ID. Its summary is the `summary` it declares, such as `Create a short URL`, which every endpoint has, since FastAPI would otherwise make one from the name with `str.title()`, such as `Resolveslug`. Its tag is the `tag` it declares, which groups it with the endpoints of the same resource. The response of success is the type of `Ok`, from the `Result[Ok, Error]` that `execute()` returns, or the type `response.model()` gives for it. The error responses are those of the errors of `Error`, which is a type alias of a union, such as `CreateShortURLError`, or a single class, grouped by status code, with `422` for the values of the request when the endpoint receives any, `400` when it receives a body, and `429` and `503`.

`add_route()` raises `LookupError` when `Error` has an error that isn't in [`ERRORS`](#errors), so a new error of a use case can't reach a client as a `500`.

Adding an endpoint is adding it to `ENDPOINTS`, after adding its use case to the [`UseCases`](bootstrap.md#use-cases) of `bootstrap`, and its new errors, if it has any, to `ERRORS`, then writing the [OpenAPI schema](#openapi) again. A new parameter of `execute()` needs no change in the API, unless it is of a type FastAPI can't read, which needs an entry in `PARAMETER_TYPES`.

## Responses

`responses.py`

A `SuccessResponse` says how an endpoint answers the `Ok` of its use case: its status code, the class of response of FastAPI, the type of what it answers, for the OpenAPI schema and the serialization, and `respond(value)`, which returns it.

| `SuccessResponse`                           | Status                   | Answers                                                                                                           |
| ------------------------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `JSONContent(status_code=200, encode=None)` | `status_code`            | The value of `Ok` as JSON. With `encode`, what `encode(value)` returns, whose type is the return type of `encode` |
| `Created(location)`                         | `201 Created`            | The value of `Ok` as JSON, with the URL `location(value)` returns in the `Location` header                        |
| `NoContent()`                               | `204 No Content`         | Nothing, whatever the value of `Ok`                                                                               |
| `Redirect(location)`                        | `307 Temporary Redirect` | A redirect to the URL `location(value)` returns, in the `Location` header                                         |

FastAPI serializes the dataclasses of the use cases with pydantic: a `UUID` as text, a `datetime` in ISO 8601, and a tuple as a list. `Created` returns a `JSONResponse`, which FastAPI doesn't serialize, so it serializes the value itself, with pydantic, in the same way.

The `Location` headers aren't in the [OpenAPI schema](#openapi) ([issue 0020](issues/0020-the-openapi-schema-has-no-location-headers.md)).

## Errors

`errors.py`

Every error is answered with an `ErrorContent`:

```json
{
  "code": "invalid_input",
  "message": "Values of the request break their rules.",
  "fields": [
    {"field": "slug", "issues": [{"code": "invalid_format"}, {"code": "too_short"}]}
  ]
}
```

- `code` tells the clients which error it is, and `message` explains it to a person. Only `code` is part of the contract: the messages can change.
- `fields` is only there for `invalid_input`. It has an item for each value that breaks its rules, in order, whose `field` is the name of the value in the request, and whose `issues` have the codes of the issues, in order. The codes are the values of [`IssueCode`](shared.md#validation), such as `too_short`, and `missing`, for a required value the request lacks.

| Error                                                       | Status                                    | `code`                            |
| ----------------------------------------------------------- | ----------------------------------------- | --------------------------------- |
| `NotAuthenticatedError`                                     | `401 Unauthorized`                        | `not_authenticated`               |
| `InvalidInputError`                                         | `422 Unprocessable Content`               | `invalid_input`                   |
| `NothingToUpdateError`                                      | `422 Unprocessable Content`               | `nothing_to_update`               |
| `ShortURLNotFoundError`                                     | `404 Not Found`                           | `shorturl_not_found`              |
| `ShortURLDeactivatedError`                                  | `404 Not Found`                           | `shorturl_deactivated`            |
| `SlugTakenError`                                            | `409 Conflict`                            | `slug_taken`                      |
| A request whose values FastAPI can't read                   | `422 Unprocessable Content`               | `invalid_input`                   |
| A body that isn't valid JSON                                | `400 Bad Request`                         | `malformed_body`                  |
| A path, or a method of a path, that no endpoint has         | `404 Not Found`, `405 Method Not Allowed` | `not_found`, `method_not_allowed` |
| [`TooManyRequestsError`](#rate-limit), raised               | `429 Too Many Requests`                   | `too_many_requests`               |
| [`UnavailableError`](use_cases.md#unavailableerror), raised | `503 Service Unavailable`                 | `unavailable`                     |
| Any other exception                                         | `500 Internal Server Error`               | `internal_error`                  |

- The errors a use case returns are answered by `error_response(error)`, from `ERRORS`, which maps each class of error to an `ErrorResponse`: its status code, code, message and headers. `response_of(error_type)` raises `LookupError` for a class that isn't there.
- `401` has the header `WWW-Authenticate: Bearer`. `429` has the header `Retry-After`, with the seconds until the client can make requests again, rounded up to a whole number. `405` has the header `Allow` that Starlette gives it, which only has the methods of one of the endpoints of the path, such as `POST` for `PUT /v1/shorturls`.
- The errors Starlette raises on its own, such as for a path or a method that no endpoint has, are answered by `http_error_handler()`, with their status, and the name of the status as the code.
- `ShortURLDeactivatedError` is only answered by the two endpoints of a slug, since `ResolveSlug` is the only use case that returns it: `GET /v1/shorturls/{id}` answers the details of a deactivated short URL to its owner, with its `status`. It is `404`, and not `410 Gone`, since `410` is for a condition that is likely to be permanent, and a deactivated short URL can be enabled again. Its code, `shorturl_deactivated`, tells it apart from a short URL that doesn't exist, instead of hiding it as `shorturl_not_found`, so the system that resolves the slug decides what to show, which may be to hide that the short URL exists. Hiding it in the API wouldn't keep the slug secret anyway: creating a short URL with it answers `slug_taken`.
- A request whose values FastAPI can't read, such as an `id` that isn't a UUID, a `limit` that isn't an integer or a `target_url` that isn't a string, gets `invalid_input`, with the same `fields` as the one of a use case. FastAPI names the issues by the types of pydantic: `missing` is kept, a type that is the value of an `IssueCode` is kept, such as the `invalid_format` of a [cursor](#cursors), and any other becomes `invalid_type`.
- `UnavailableError` is logged as a warning, with the exception and its cause, which say what failed. Starlette raises any other exception again after its response, so the server logs it.

## Authentication

`authentication.py`

The service doesn't issue access tokens: it receives them, issued by someone else, and only verifies them, through the `AccessTokenVerifier` abstraction. Its `verify(token)` returns the `UserID` of the user the token was issued to, or `None` when the token isn't valid, and may raise `UnavailableError` when something the verification needs is unavailable, such as the keys of the issuer.

`AccessTokenCurrentUser(token, verifier)` implements the [`CurrentUser`](use_cases.md#current-user) of a request. `get_id()` returns `None` when `token` is `None`, without verifying anything, and otherwise what `verify(token)` returns.

The token is verified only when the use case asks for the user, and a token that isn't valid is the same as no token: a use case that requires a user returns `NotAuthenticatedError`, answered with `401`.

## Rate limit

`rate_limit.py`

Every endpoint counts each request under the IP address of its client, and a request over the limit of its IP address gets `too_many_requests`, without its use case being built. The endpoints share the count, so the requests of an IP address to any of them add up. The [health check](#health-check) isn't limited, nor is a path that no endpoint has.

The API counts the requests through the `RateLimiter` abstraction. Its `hit(key)` counts a request of the key, and returns `None` when the key is within its limit, and otherwise how long until the key can make requests again, as a `timedelta`. The limit, and how the requests are counted, are up to the implementation, [`InMemoryRateLimiter`](infra.md#rate-limit), which [`bootstrap`](bootstrap.md#the-application) builds with the limit of the [settings](bootstrap.md#settings).

`limit_by_ip(rate_limiter)` returns the dependency of FastAPI that `create_app()` gives to the router of the endpoints. For each request, it calls `hit()` with the IP address of the client, and raises `TooManyRequestsError`, with the time `hit()` returned, when that isn't `None`. It is a coroutine, so FastAPI runs it in the event loop, and not in a thread, where two requests could count at the same time.

- The IP address is the one the server gives as the client's. Behind a proxy, it is the address of the proxy, unless the server trusts the proxy and takes the address of the client from what the proxy sends (see [Running](bootstrap.md#running)).
- A request without the address of its client, which the server may give for a connection that isn't TCP, such as one through a Unix socket, isn't limited.
- The dependency runs before FastAPI reads the values of the request, so a request whose values can't be read is counted too. A request whose body isn't valid JSON is the exception: FastAPI answers it with `malformed_body` before the dependency runs, so it isn't counted.

## Use cases

`use_case_factory.py`

The use cases that receive a `CurrentUser` are built for each request, since the user is the one of the request. `UseCaseFactory.build(use_case, current_user)` returns the use case of the class `use_case`, built with `current_user`, which the endpoint runs. The API doesn't build the use cases itself: [`UseCases`](bootstrap.md#use-cases), in `bootstrap`, does, with the implementations of their abstractions.

## Health check

`health_check.py`

`GET /v1/health` tells an orchestrator or a load balancer whether the service is able to answer. It isn't one of `ENDPOINTS`, since it runs no use case: `add_health_check_route(router, health_check)` adds it, and it awaits `check()` of the `HealthCheck` that `create_app()` receives. `check()` returns when the service is able to answer, and raises `UnavailableError` when something it needs to answer is unavailable.

| `check()`                  | Answers                                            |
| -------------------------- | -------------------------------------------------- |
| Returns                    | `204 No Content`                                   |
| Raises `UnavailableError`  | `503 Service Unavailable`, with `unavailable`      |
| Raises any other exception | `500 Internal Server Error`, with `internal_error` |

- It doesn't read the access token, and it isn't [rate limited](#rate-limit), so an orchestrator or a load balancer that checks it often doesn't get `too_many_requests`. The OpenAPI schema documents it as `CheckHealth`, in the tag `Health`, with a summary, `204` and `503`.
- [`SQLAlchemyHealthCheck`](infra.md#health-check), the implementation `bootstrap` gives it, checks that the database answers. So, as a liveness probe, one that restarts the service when it fails, a failure of the database would restart the service too.

## Cursors

`cursors.py` and `shorturl_page_content.py`

A [`ShortURLCursor`](use_cases.md#shorturlcursor) travels as an opaque text. `encode_cursor(cursor)` returns the base64url, without padding, of the `created_at` of the cursor in ISO 8601 and its `id`, separated by a comma, which a URL carries as it is. `decode_cursor(text)` returns the cursor back, or `None` for a text that `encode_cursor()` doesn't return: one that isn't base64url, doesn't have two parts, or whose `created_at` isn't a datetime with a timezone, or whose `id` isn't a UUID.

`CursorParameter` is how a request carries a `ShortURLCursor`, in `PARAMETER_TYPES`: a text, which FastAPI turns into the cursor with `decode_cursor()`, and answers with an `invalid_format` issue when it returns `None`.

`ShortURLPageContent.from_page(page)` is what `GET /v1/shorturls` answers for a [`ShortURLPage`](use_cases.md#shorturlpage): its `items`, and its `next_cursor` encoded, or `None` when there is no next page.

## CORS

The API answers no CORS headers, so a web page of another origin can't call it from the browser, such as with `fetch`. CORS only applies to those calls, and not to navigations, such as following a short link and its redirect. The API is meant to be called by the servers of the systems that use the shortener, and the redirect to be followed by the browser of the user, so neither needs CORS. An application in the browser that calls the API directly, from another origin, would need it, with the origins it allows.

## Open questions

Decisions to make during this phase. There are none at the moment.
