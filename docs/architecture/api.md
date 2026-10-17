# API

The API is the entry point of the HTTP requests: it answers them by running the [use cases](use_cases.md). It lives in `shortener/api/`, is built with FastAPI, and imports only from the use cases, the [domain](domain.md) and [`shortener/shared/`](shared.md). What it needs from outside, such as verifying access tokens, it defines as abstractions, which [`infra`](infra.md) implements and [`bootstrap`](bootstrap.md) gives to it.

What the API answers, seen by its clients, is in [docs/service/api.md](../service/api.md): this document describes how the code does it.

## Overview

```
shortener/api/
├── app.py                     create_app()
├── prefix.py                  PREFIX
├── endpoints.py               ENDPOINTS
├── endpoint.py                Endpoint, UseCase, add_route() and PARAMETER_TYPES
├── responses.py               SuccessResponse, JSONContent, Created, NoContent and Redirect
├── errors.py                  ERRORS, ErrorResponse, ErrorContent, error_response() and the
│                              handlers of exceptions
├── openapi.py                 documented_headers()
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

`create_app(use_cases, access_token_verifier, rate_limiter, health_check, endpoints=ENDPOINTS, lifespan=None)` returns the FastAPI application. It adds a route for each [endpoint](#endpoints), and the one of the [health check](#health-check), under `PREFIX` (`/api/v1`), with the [rate limit](#rate-limit) of `rate_limiter` on the endpoints, and the handlers of the exceptions that become [errors](#errors). `lifespan` is the one of FastAPI, for what has to run when the application starts and stops. It raises `LookupError` when the use case of an endpoint may return an error the API doesn't answer (see [How an endpoint works](#how-an-endpoint-works)), so the application doesn't start.

## OpenAPI

`create_app()` turns off the OpenAPI schema and the documentation that FastAPI serves, so `/openapi.json`, `/docs` and `/redoc` answer `not_found`, like any path that no route has. The schema is in [openapi.yaml](../service/openapi.yaml), which `poetry run task openapi` writes from what `create_app()` gives, and a test of `tests/test_api/test_app.py` fails when the file isn't the schema of the code. So a change to what the API receives or answers, such as an endpoint, a parameter or an error, comes with the file written again.

Whoever consumes the API reads the schema where its code is, without running the API, opens it in any tool that previews OpenAPI or gives it to an agent, and sees its changes in the diff. And the API running in production doesn't expose it.

`documented_headers(descriptions)`, in `openapi.py`, returns the headers of a response for the schema, from the description of each one, with the value of each one as a text. It returns nothing for no headers, since FastAPI would document an empty set of them. The [responses of success](#responses) and the [errors](#errors) describe their headers with it.

## Endpoints

`endpoints.py`

`ENDPOINTS` declares each endpoint of the API, with the use case it runs and how it answers its `Ok`:

| Method and path                       | Use case                                                             | Response                                                |
| ------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------- |
| `GET /api/v1/slugs/{slug}`            | [`ResolveSlug`](use_cases.md#resolveslug)                            | `JSONContent()`, with the `ResolvedSlug`                |
| `GET /api/v1/slugs/{slug}/redirect`   | [`ResolveSlug`](use_cases.md#resolveslug), named `RedirectSlug`      | `Redirect`, to its `target_url`                         |
| `POST /api/v1/shorturls`              | [`CreateShortURL`](use_cases.md#createshorturl)                      | `Created`, with the path of the short URL               |
| `GET /api/v1/shorturls`               | [`ListShortURLs`](use_cases.md#listshorturls)                        | `JSONContent`, with a [`ShortURLPageContent`](#cursors) |
| `GET /api/v1/shorturls/{id}`          | [`GetShortURL`](use_cases.md#getshorturl)                            | `JSONContent()`                                         |
| `PATCH /api/v1/shorturls/{id}`        | [`UpdateShortURL`](use_cases.md#updateshorturl)                      | `JSONContent()`                                         |
| `POST /api/v1/shorturls/{id}/enable`  | [`EnableShortURL`](use_cases.md#enableshorturl-and-disableshorturl)  | `JSONContent()`                                         |
| `POST /api/v1/shorturls/{id}/disable` | [`DisableShortURL`](use_cases.md#enableshorturl-and-disableshorturl) | `JSONContent()`                                         |
| `DELETE /api/v1/shorturls/{id}`       | [`DeleteShortURL`](use_cases.md#deleteshorturl)                      | `NoContent()`                                           |

What each one receives and answers follows from its use case, by the rules of [How an endpoint works](#how-an-endpoint-works):

- The two endpoints of a slug run `ResolveSlug`, so both count the resolution. Why there are two is in [Overview](../service/api.md#overview).
- Every endpoint but the two of a slug reads the [access token](#authentication), since its use case takes a `CurrentUser`.
- `slug`, and the `target_url` of a `PATCH`, default to `None` in `execute()`, so a `null` is the same as leaving them out: `POST /api/v1/shorturls` generates the slug, and `PATCH /api/v1/shorturls/{id}` doesn't change them. A `PATCH` with no value to change gets `nothing_to_update`. The `target_url` of a `POST` has no default, so leaving it out, or sending it as `null`, gets `missing`.
- `limit` is 20 when the query leaves it out, the default of `ListShortURLs.execute()`.
- The `Location` of `POST /api/v1/shorturls` is the path of the new short URL, `/api/v1/shorturls/{id}`, with the `id` of its `ShortURLDetails`, which `GET /api/v1/shorturls/{id}` answers. The path of a short URL is written once, in `endpoints.py`.
- The OpenAPI schema groups the two endpoints of a slug in the tag `Slugs`, and the others in `Short URLs`.

## How an endpoint works

`endpoint.py`

`Endpoint(method, path, use_case, response=JSONContent(), *, summary, tag, name=None)` declares an endpoint, and `add_route()` adds it to the router of FastAPI. Only the method, the path, the use case, how to answer its `Ok`, a summary and a tag are declared, and, when it needs one, a name: what the endpoint receives, who makes the request and how errors are answered come from the use case. Each `Endpoint` builds its own default `JSONContent`.

`use_case` is a class that implements `UseCase`, a `Protocol` whose `execute()` returns a `Result`: the endpoint reads what it receives from the signature of `execute()`, and what it answers from the `Result`.

**Parameters.** Each parameter of `execute()` becomes one of the request, with its name, its type and its default:

- When its name is in the path, such as `{id}`, it comes from the path.
- Otherwise, it comes from the query when the method is `GET` or `DELETE`, and from a field of the JSON object of the body for the other methods.
- It is required when `execute()` has no default for it, and a `null` for it in the body is the same as leaving it out. Otherwise, a request that leaves it out gives the default of `execute()`.
- FastAPI reads it as the type of `execute()`, such as a `UUID` from the text of the path, or an `int` from the text of the query. A type that is in `PARAMETER_TYPES` is read as the type it maps to instead, which is how a request carries a [`ShortURLCursor`](#cursors). In a union, such as `ShortURLCursor | None`, each member is replaced.

Since the name of a parameter of `execute()` is the name of its value in the request, the `field` of a [`FieldError`](use_cases.md#errors-of-the-use-cases) of the use case is the name the client sent.

**Access token.** When the constructor of the use case takes a `CurrentUser`, the endpoint reads the `Authorization` header, with the `Bearer` scheme, and the OpenAPI schema says the endpoint takes a bearer token, `AccessToken`, in the format of a JWT, the one [`JWTAccessTokenVerifier`](infra.md#access-tokens) verifies. Otherwise, it doesn't read the header.

**Running.** For each request, the endpoint:

1. builds an [`AccessTokenCurrentUser`](#authentication) with the token, or with `None` when the header is missing, isn't of the `Bearer` scheme, or isn't read;
2. asks the [`UseCaseFactory`](#use-cases) for the use case, with that current user;
3. awaits `execute()`, with the values of the request as keyword arguments;
4. answers `Ok` with its [`SuccessResponse`](#responses), and `Err` with [`error_response()`](#errors).

FastAPI reads the values of the request before step 1, so a request whose values it can't read gets an [error](#errors) without the use case being built. It runs the [rate limit](#rate-limit) after parsing the JSON of the body and before reading the values, so a request over the limit gets `too_many_requests` even when its values can't be read.

**OpenAPI.** The name of the endpoint is its name and operation ID, and is the name of its use case when `name` is `None`. Two endpoints of the same use case need different names, since FastAPI warns about a repeated operation ID. Its summary is the `summary` it declares, such as `Create a short URL`, which every endpoint has, since FastAPI would otherwise make one from the name with `str.title()`, such as `Resolveslug`. Its tag is the `tag` it declares, which groups it with the endpoints of the same resource. The response of success is the type of `Ok`, from the `Result[Ok, Error]` that `execute()` returns, or the type `response.model()` gives for it, and its description is the phrase of its status, such as `Created`, with the headers `response` describes. The error responses are those of the errors of `Error`, which is a type alias of a union, such as `CreateShortURLError`, or a single class, grouped by status code, with the headers they describe, with `422` for the values of the request when the endpoint receives any, `400` when it receives a body, and `429` and `503`.

`add_route()` raises `LookupError` when `Error` has an error that isn't in [`ERRORS`](#errors), so a new error of a use case can't reach a client as a `500`.

Adding an endpoint is adding it to `ENDPOINTS`, after adding its use case to the [`UseCases`](bootstrap.md#use-cases) of `bootstrap`, and its new errors, if it has any, to `ERRORS`, then writing the [OpenAPI schema](#openapi) again and describing it in [docs/service/api.md](../service/api.md#endpoints). A new parameter of `execute()` needs no change in the API, unless it is of a type FastAPI can't read, which needs an entry in `PARAMETER_TYPES`.

## Responses

`responses.py`

A `SuccessResponse` says how an endpoint answers the `Ok` of its use case: its status code, as a read-only property, the class of response of FastAPI, the type of what it answers, for the OpenAPI schema and the serialization, `header_descriptions`, with the description of each header it answers, also for the schema, and `respond(value)`, which returns it.

| `SuccessResponse`                           | Status                   | Answers                                                                                                           |
| ------------------------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `JSONContent(status_code=200, encode=None)` | `status_code`            | The value of `Ok` as JSON. With `encode`, what `encode(value)` returns, whose type is the return type of `encode` |
| `Created(location)`                         | `201 Created`            | The value of `Ok` as JSON, with the URL `location(value)` returns in the `Location` header                        |
| `NoContent()`                               | `204 No Content`         | Nothing, whatever the value of `Ok`                                                                               |
| `Redirect(location)`                        | `307 Temporary Redirect` | A redirect to the URL `location(value)` returns, in the `Location` header                                         |

FastAPI serializes the dataclasses of the use cases with pydantic: a `UUID` as text, a `datetime` in ISO 8601, and a tuple as a list. `Created` returns a `JSONResponse`, which FastAPI doesn't serialize, so it serializes the value itself, with pydantic, in the same way.

`Created` and `Redirect` describe their `Location` in `header_descriptions`, and `JSONContent` and `NoContent` describe no header.

## Errors

`errors.py`

Every error is answered with an `ErrorContent`, a model of pydantic with `code`, `message` and, only for `invalid_input`, `fields`, whose format and codes are in [Errors](../service/api.md#errors).

The errors a use case returns are answered by `error_response(error)`, from `ERRORS`, which maps each class of error to an `ErrorResponse`: its status code, code, message and headers, and, in `header_descriptions`, the description of each header it answers, for the OpenAPI schema. `response_of(error_type)` raises `LookupError` for a class that isn't there. These are the classes, and their codes:

| Class                      | `code`                 |
| -------------------------- | ---------------------- |
| `NotAuthenticatedError`    | `not_authenticated`    |
| `InvalidInputError`        | `invalid_input`        |
| `NothingToUpdateError`     | `nothing_to_update`    |
| `ShortURLNotFoundError`    | `shorturl_not_found`   |
| `ShortURLDeactivatedError` | `shorturl_deactivated` |
| `SlugTakenError`           | `slug_taken`           |

The other errors are answered by the handlers of exceptions that `create_app()` adds:

| Handler                       | Handles                                                                                | `code`                                        |
| ----------------------------- | -------------------------------------------------------------------------------------- | --------------------------------------------- |
| `request_error_handler()`     | `RequestValidationError`: a request whose values FastAPI can't read                    | `malformed_body`, or `invalid_input`          |
| `http_error_handler()`        | The `HTTPException`s Starlette raises on its own, such as for a path that no route has | The name of the status, such as `not_found`   |
| `too_many_requests_handler()` | [`TooManyRequestsError`](#rate-limit)                                                  | `too_many_requests`, from `TOO_MANY_REQUESTS` |
| `unavailable_handler()`       | [`UnavailableError`](use_cases.md#unavailableerror)                                    | `unavailable`, from `UNAVAILABLE`             |
| `internal_error_handler()`    | Any other exception                                                                    | `internal_error`, from `INTERNAL_ERROR`       |

- `request_error_handler()` answers `malformed_body` when the body isn't valid JSON, and otherwise `invalid_input`, with the same `fields` as the one of a use case. FastAPI names the issues by the types of pydantic: `missing` is kept, a type that is the value of an [`IssueCode`](shared.md#validation) is kept, such as the `invalid_format` of a [cursor](#cursors), and any other becomes `invalid_type`.
- `too_many_requests_handler()` answers `Retry-After` with the time of the error rounded up to whole seconds. The OpenAPI schema documents it from the `header_descriptions` of `TOO_MANY_REQUESTS`, as it does `WWW-Authenticate` from the ones of `ERRORS`.
- `http_error_handler()` keeps the headers Starlette gives the error, such as the `Allow` of a `405`.
- `unavailable_handler()` logs the error as a warning, with the exception and its cause, which say what failed. Starlette raises any other exception again after its response, so the server logs it.
- `ShortURLDeactivatedError` is only answered by the two endpoints of a slug, since `ResolveSlug` is the only use case that returns it: `GET /api/v1/shorturls/{id}` answers the details of a deactivated short URL to its owner, with its `status`.

## Authentication

`authentication.py`

The API receives access tokens, issued by someone else, and only verifies them, through the `AccessTokenVerifier` abstraction. Its `verify(token)` returns the `UserID` of the user the token was issued to, or `None` when the token isn't valid, and may raise `UnavailableError` when something the verification needs is unavailable, such as the keys of the issuer.

`AccessTokenCurrentUser(token, verifier)` implements the [`CurrentUser`](use_cases.md#current-user) of a request. `get_id()` returns `None` when `token` is `None`, without verifying anything, and otherwise what `verify(token)` returns.

The token is verified only when the use case asks for the user, and a token that isn't valid is the same as no token: a use case that requires a user returns `NotAuthenticatedError`, answered with `401`.

## Rate limit

`rate_limit.py`

Every endpoint counts each request under the IP address of its client, and a request over the limit of its IP address gets `too_many_requests`, without its use case being built. The endpoints share the count. What that means for the clients is in [Rate limit](../service/api.md#rate-limit).

The API counts the requests through the `RateLimiter` abstraction. Its `hit(key)` counts a request of the key, and returns `None` when the key is within its limit, and otherwise how long until the key can make requests again, as a `timedelta`. The limit, and how the requests are counted, are up to the implementation, [`InMemoryRateLimiter`](infra.md#rate-limit), which [`bootstrap`](bootstrap.md#the-application) builds with the limit of the [settings](bootstrap.md#settings).

`limit_by_ip(rate_limiter)` returns the dependency of FastAPI that `create_app()` gives to the router of the endpoints, so it doesn't run for the [health check](#health-check), which has a router of its own, nor for a path that no route has. For each request, it calls `hit()` with the IP address the server gives as the client's, `request.client.host`, and raises `TooManyRequestsError`, with the time `hit()` returned, when that isn't `None`. It is a coroutine, so FastAPI runs it in the event loop, and not in a thread, where two requests could count at the same time.

- A request without the address of its client, whose `request.client` is `None`, isn't counted.
- The dependency runs before FastAPI reads the values of the request, so a request whose values can't be read is counted too. A request whose body isn't valid JSON is the exception: FastAPI answers it with `malformed_body` before the dependency runs, so it isn't counted.

## Use cases

`use_case_factory.py`

The use cases that receive a `CurrentUser` are built for each request, since the user is the one of the request. `UseCaseFactory.build(use_case, current_user)` returns the use case of the class `use_case`, built with `current_user`, which the endpoint runs. The API doesn't build the use cases itself: [`UseCases`](bootstrap.md#use-cases), in `bootstrap`, does, with the implementations of their abstractions.

## Health check

`health_check.py`

`GET /api/v1/health` isn't one of `ENDPOINTS`, since it runs no use case: `add_health_check_route(router, health_check)` adds it, on a router without the rate limit, and it awaits `check()` of the `HealthCheck` that `create_app()` receives. `check()` returns when the service is able to answer, and raises `UnavailableError` when something it needs to answer is unavailable.

| `check()`                  | Answers                                            |
| -------------------------- | -------------------------------------------------- |
| Returns                    | `204 No Content`                                   |
| Raises `UnavailableError`  | `503 Service Unavailable`, with `unavailable`      |
| Raises any other exception | `500 Internal Server Error`, with `internal_error` |

- It doesn't read the access token. The OpenAPI schema documents it as `CheckHealth`, in the tag `Health`, with a summary, `204` and `503`.
- [`SQLAlchemyHealthCheck`](infra.md#health-check), the implementation `bootstrap` gives it, checks that the database answers.

## Cursors

`cursors.py` and `shorturl_page_content.py`

A [`ShortURLCursor`](use_cases.md#shorturlcursor) travels as an opaque text. `encode_cursor(cursor)` returns the base64url, without padding, of the `created_at` of the cursor in ISO 8601 and its `id`, separated by a comma, which a URL carries as it is. `decode_cursor(text)` returns the cursor back, or `None` for a text that `encode_cursor()` doesn't return: one that isn't base64url, doesn't have two parts, or whose `created_at` isn't a datetime with a timezone, or whose `id` isn't a UUID.

`CursorParameter` is how a request carries a `ShortURLCursor`, in `PARAMETER_TYPES`: a text, which FastAPI turns into the cursor with `decode_cursor()`, and answers with an `invalid_format` issue when it returns `None`.

`ShortURLPageContent.from_page(page)` is what `GET /api/v1/shorturls` answers for a [`ShortURLPage`](use_cases.md#shorturlpage): its `items`, and its `next_cursor` encoded, or `None` when there is no next page.
