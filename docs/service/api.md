# HTTP API

What the HTTP API offers and how it behaves, seen by whoever calls it. The exact schema of each request and response is in [openapi.yaml](openapi.yaml), and how the code does what this document describes is in [the architecture of the API](../architecture/api.md).

## Overview

Every route is under `/api/v1`, and the bodies of its requests and responses are JSON.

| Method and path                       | What it does                                                                   | Access token |
| ------------------------------------- | ------------------------------------------------------------------------------ | ------------ |
| `GET /api/v1/slugs/{slug}`            | [Answers the target URL of a slug](#resolve-a-slug)                            | No           |
| `GET /api/v1/slugs/{slug}/redirect`   | [Redirects to the target URL of a slug](#redirect-to-the-target-url-of-a-slug) | No           |
| `POST /api/v1/shorturls`              | [Creates a short URL](#create-a-short-url)                                     | Yes          |
| `GET /api/v1/shorturls`               | [Lists the short URLs of the user](#list-the-short-urls-of-the-user)           | Yes          |
| `GET /api/v1/shorturls/{id}`          | [Answers a short URL](#get-a-short-url)                                        | Yes          |
| `PATCH /api/v1/shorturls/{id}`        | [Changes the target URL or the slug](#update-a-short-url)                      | Yes          |
| `POST /api/v1/shorturls/{id}/enable`  | [Activates a short URL](#enable-and-disable-a-short-url)                       | Yes          |
| `POST /api/v1/shorturls/{id}/disable` | [Deactivates a short URL](#enable-and-disable-a-short-url)                     | Yes          |
| `DELETE /api/v1/shorturls/{id}`       | [Deletes a short URL](#delete-a-short-url)                                     | Yes          |
| `GET /api/v1/health`                  | [Tells whether the service can answer](#health-check)                          | No           |

The routes of a slug need no access token, since anyone can resolve a slug, and the routes of the short URLs are for their owners. The shortener serves other systems, which decide how to resolve a slug: one that wants to decide what to do with the target URL, such as showing a page before it redirects, asks for it, and one that wants the redirect done asks for the redirect.

Since every route is under `/api/v1`, a slug never shares a path with a route, and no slug has to be reserved. A domain of short links, where `/{slug}` redirects, is a proxy in front of the service (see [Running](running.md#behind-a-proxy)).

## Access tokens

The service doesn't issue access tokens, nor manage users: a system responsible for the identities of the users issues them, and the service only verifies them. An endpoint that needs a user reads the access token from the `Authorization` header, with the `Bearer` scheme:

```
Authorization: Bearer <access token>
```

The access token is a JWT, which is valid when:

- it is signed with one of the algorithms of the [configuration](configuration.md#the-api), by its key, or by one of the keys the issuer publishes at a JWKS URL;
- it has `exp`, `iss`, `aud` and `sub`: `iss` is the issuer of the configuration, `aud` is its audience, or a list that has it, and `sub` is the UUID of the user;
- it hasn't expired, and, when it has `nbf` or `iat`, they aren't in the future, both with a tolerance of `JWT_LEEWAY`, 60 seconds by default, for the difference between the clocks of the issuer and of the service.

A missing token, one of another scheme, such as `Basic`, and one that isn't valid are all the same as no token: an endpoint that needs a user answers `401` with `not_authenticated`. When the keys of the issuer can't be fetched from its JWKS URL, or what it answers isn't a set of keys, the endpoint answers `503` with `unavailable`. The routes of a slug and the health check don't read the header.

The service checks nothing about the user besides the token: it doesn't know whether the user still exists (see [Known limitations](#known-limitations)).

## Short URLs

A short URL is a slug that points to a target URL, and belongs to the user who created it, its owner. The owner is the only one who sees it, lists it, changes it or deletes it: a short URL of another user gets the same `404` with `shorturl_not_found` as one that doesn't exist.

| Field              | Value                                                               |
| ------------------ | ------------------------------------------------------------------- |
| `id`               | The ID of the short URL, a UUID                                     |
| `slug`             | The short path that resolves to the target URL                      |
| `target_url`       | Where the slug leads                                                |
| `owner_id`         | The UUID of the owner, the `sub` of their access token              |
| `status`           | `active` or `deactivated`                                           |
| `resolution_count` | How many times the slug was resolved while the short URL was active |
| `created_at`       | When it was created                                                 |
| `last_resolved_at` | When the slug was last resolved, or `null` when it never was        |

```json
{
  "id": "0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a20",
  "slug": "my-slug",
  "target_url": "https://example.com/a/long/path",
  "owner_id": "0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10",
  "status": "active",
  "resolution_count": 3,
  "created_at": "2026-01-01T00:00:00Z",
  "last_resolved_at": "2026-01-02T12:30:00Z"
}
```

The IDs are text, and the datetimes are in ISO 8601, in UTC, with `Z`.

### Slugs

- A slug has from 3 to 30 characters, which are ASCII letters, digits, `_` and `-`.
- Slugs are unique, and case-sensitive: `abc` and `ABC` are different slugs.
- When the request doesn't give one, the service generates it: 6 random ASCII letters and digits. When the generated slug is taken, it tries another, up to 10 slugs in all, and then answers `500` with `internal_error`.

### Target URLs

- A target URL is an `https` URL with a host, such as `https://example.com/path?query`. The scheme is case-insensitive.
- It can't have spaces, nor characters that are invisible or mean nothing in a URL, such as tabs, line breaks, other control characters and zero-width spaces, which could make it lead somewhere other than where it looks to. [TargetURL](../architecture/domain.md#targeturl) lists them, with the reason for each.
- Letters of any script, symbols and emoji are accepted, as in `https://例え.jp`.
- Nothing else is checked: the host isn't validated, so `https://exa..mple.com` is accepted.

The rules of slugs and target URLs can change, and a value accepted under older rules keeps working: it still resolves, lists and loads. Only the values a request sends are checked against the current rules.

### Status and resolutions

- A short URL is created `active`. [Disable](#enable-and-disable-a-short-url) makes it `deactivated`, and enable makes it `active` again.
- Resolving the slug of an active short URL, by either [route of a slug](#resolve-a-slug), counts a resolution: it adds 1 to `resolution_count` and sets `last_resolved_at`. The service counts the resolutions it answers, not the visits: it doesn't know whether the client opened the target URL.
- Resolving the slug of a deactivated short URL answers `404` with `shorturl_deactivated`, and counts nothing. It is `404`, and not `410 Gone`, since `410` is for a condition that is likely to be permanent, and a deactivated short URL can be enabled again. Its code tells it apart from a slug that doesn't exist, instead of hiding it as `shorturl_not_found`, so the system that resolves the slug decides what to show, which may be to hide that the short URL exists. Hiding it in the API wouldn't keep the slug secret anyway: creating a short URL with it answers `slug_taken`.

## Endpoints

Each endpoint answers the errors of its section, and also `429` when the client is over its [rate limit](#rate-limit) and `503` when the service is [unavailable](#errors). An endpoint that receives values answers `422` with `invalid_input` for a value of the wrong type, such as an `id` that isn't a UUID, and one that receives a body answers `400` with `malformed_body` for a body that isn't valid JSON. The [Errors](#errors) section describes them all.

The checks of a request run in this order, and the first one that fails answers: the JSON of the body, the rate limit, the types of the values, the access token, the rules of the values, and then what the operation finds, such as a short URL that doesn't exist.

### Resolve a slug

`GET /api/v1/slugs/{slug}` answers `200` with the target URL, and [counts the resolution](#status-and-resolutions):

```json
{"target_url": "https://example.com/a/long/path"}
```

| Status | `code`                 | When                                     |
| ------ | ---------------------- | ---------------------------------------- |
| `404`  | `shorturl_not_found`   | No short URL has the slug                |
| `404`  | `shorturl_deactivated` | The short URL of the slug is deactivated |

Any slug is looked up, even one that breaks the current rules, so a slug created under older rules still resolves.

### Redirect to the target URL of a slug

`GET /api/v1/slugs/{slug}/redirect` answers `307 Temporary Redirect` to the target URL, in the `Location` header, and counts the resolution. It answers the same errors as [Resolve a slug](#resolve-a-slug), as JSON.

The redirect is temporary, so the clients don't keep it: each visit asks the service again, which counts the resolution, and follows the changes of the target URL and the deactivations.

### Create a short URL

`POST /api/v1/shorturls` creates a short URL owned by the user of the access token:

```json
{"target_url": "https://example.com/a/long/path", "slug": "my-slug"}
```

`slug` is optional: without it, or with `null`, the service [generates one](#slugs). It answers `201`, with the [short URL](#short-urls), and its path, `/api/v1/shorturls/{id}`, in the `Location` header.

| Status | `code`              | When                                                                                                                           |
| ------ | ------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `401`  | `not_authenticated` | There is no valid access token                                                                                                 |
| `422`  | `invalid_input`     | `target_url` is missing or `null`, or `target_url` or `slug` break the rules of [target URLs](#target-urls) or [slugs](#slugs) |
| `409`  | `slug_taken`        | Another short URL has the slug                                                                                                 |

### List the short URLs of the user

`GET /api/v1/shorturls` answers `200` with a page of the short URLs of the user, newest first:

```
{"items": [<short URL>, ...], "next_cursor": "MjAyNi0wMS0wMVQwMDowMDowMCswMDowMCwwMTk5YjJjNC03YTNlLTdjMWEtOWI1ZS0zZjJkNGM2YjhhMjA"}
```

| Query    | Value                                                                   |
| -------- | ----------------------------------------------------------------------- |
| `limit`  | The most short URLs the page has, from 1 to 100. 20 when it is left out |
| `cursor` | The `next_cursor` of the previous page, to read the next one            |

- `next_cursor` is `null` on the last page. A user with no short URLs gets a page with no items.
- A cursor is opaque: a client only sends back what a page answered. It keeps working after the short URL it came from is deleted or changed.
- A page doesn't skip or repeat short URLs when others are created or deleted between pages.

| Status | `code`              | When                                                                               |
| ------ | ------------------- | ---------------------------------------------------------------------------------- |
| `401`  | `not_authenticated` | There is no valid access token                                                     |
| `422`  | `invalid_input`     | `limit` isn't an integer from 1 to 100, or `cursor` isn't one that a page answered |

### Get a short URL

`GET /api/v1/shorturls/{id}` answers `200` with the [short URL](#short-urls), also when it is deactivated.

| Status | `code`               | When                                                    |
| ------ | -------------------- | ------------------------------------------------------- |
| `401`  | `not_authenticated`  | There is no valid access token                          |
| `404`  | `shorturl_not_found` | The short URL doesn't exist, or belongs to another user |

### Update a short URL

`PATCH /api/v1/shorturls/{id}` changes the target URL, the slug, or both, and answers `200` with the [short URL](#short-urls):

```json
{"target_url": "https://example.com/another/path", "slug": "another-slug"}
```

A value that is left out, or `null`, isn't changed. Both change together or not at all: when the new slug is taken, the target URL doesn't change either. When the slug changes, the old one is free from then on.

| Status | `code`               | When                                                                                     |
| ------ | -------------------- | ---------------------------------------------------------------------------------------- |
| `401`  | `not_authenticated`  | There is no valid access token                                                           |
| `422`  | `nothing_to_update`  | The request has neither `target_url` nor `slug`                                          |
| `422`  | `invalid_input`      | `target_url` or `slug` break the rules of [target URLs](#target-urls) or [slugs](#slugs) |
| `404`  | `shorturl_not_found` | The short URL doesn't exist, or belongs to another user                                  |
| `409`  | `slug_taken`         | Another short URL has the slug                                                           |

The status doesn't change here, but with [enable and disable](#enable-and-disable-a-short-url).

### Enable and disable a short URL

`POST /api/v1/shorturls/{id}/enable` makes the short URL active, and `POST /api/v1/shorturls/{id}/disable` deactivates it. Both answer `200` with the [short URL](#short-urls), also when it already had that status. They receive no body.

| Status | `code`               | When                                                    |
| ------ | -------------------- | ------------------------------------------------------- |
| `401`  | `not_authenticated`  | There is no valid access token                          |
| `404`  | `shorturl_not_found` | The short URL doesn't exist, or belongs to another user |

### Delete a short URL

`DELETE /api/v1/shorturls/{id}` deletes the short URL, and answers `204` with no content. Its slug is free from then on.

| Status | `code`               | When                                                    |
| ------ | -------------------- | ------------------------------------------------------- |
| `401`  | `not_authenticated`  | There is no valid access token                          |
| `404`  | `shorturl_not_found` | The short URL doesn't exist, or belongs to another user |

### Health check

`GET /api/v1/health` tells an orchestrator or a load balancer whether the service can answer, by checking that the database answers:

| Status | `code`           | When                                                                                    |
| ------ | ---------------- | --------------------------------------------------------------------------------------- |
| `204`  |                  | The database answers                                                                    |
| `503`  | `unavailable`    | The database can't answer now, such as when it can't be reached                         |
| `500`  | `internal_error` | The database fails in a way that trying again won't fix, such as one that doesn't exist |

It reads no access token and has no [rate limit](#rate-limit), so a client that checks it often doesn't get `429`. How to use it in an orchestrator is in [Running](running.md#health-checks).

## Errors

Every error is answered with the same JSON:

```json
{
  "code": "invalid_input",
  "message": "Values of the request break their rules.",
  "fields": [
    {"field": "slug", "issues": [{"code": "invalid_format"}, {"code": "too_short"}]}
  ]
}
```

`code` tells which error it is, and `message` explains it to a person. Only `code` is part of the contract: the messages can change.

| Status | `code`                 | When                                                                                                                                        |
| ------ | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `400`  | `malformed_body`       | The body isn't valid JSON                                                                                                                   |
| `401`  | `not_authenticated`    | The endpoint needs a user, and the request has no valid [access token](#access-tokens)                                                      |
| `404`  | `shorturl_not_found`   | The short URL doesn't exist, or belongs to another user                                                                                     |
| `404`  | `shorturl_deactivated` | The short URL of the slug is deactivated                                                                                                    |
| `404`  | `not_found`            | No route has the path                                                                                                                       |
| `405`  | `method_not_allowed`   | The path has routes, but none with the method                                                                                               |
| `409`  | `slug_taken`           | Another short URL has the slug                                                                                                              |
| `422`  | `invalid_input`        | Values of the request are missing, of the wrong type, or break their rules                                                                  |
| `422`  | `nothing_to_update`    | An update has no value to change                                                                                                            |
| `429`  | `too_many_requests`    | The client is over its [rate limit](#rate-limit)                                                                                            |
| `500`  | `internal_error`       | The service failed, in a way that trying again won't fix                                                                                    |
| `503`  | `unavailable`          | Something the service needs, such as the database or the keys of the issuer of the tokens, can't answer now. Trying again later may succeed |

`fields` is only in `invalid_input`. It has an item for each value that is wrong, in order, whose `field` is the name of the value in the request, such as `slug` or `limit`, and whose `issues` have a code for each rule the value breaks:

| Issue            | The value...                                               |
| ---------------- | ---------------------------------------------------------- |
| `missing`        | is required, and the request lacks it                      |
| `invalid_type`   | isn't of its type, such as a `limit` that isn't an integer |
| `invalid_format` | doesn't have its format, such as a slug with a space       |
| `too_short`      | is shorter than its minimum length                         |
| `too_long`       | is longer than its maximum length                          |
| `too_small`      | is smaller than its minimum, such as a `limit` of 0        |
| `too_large`      | is larger than its maximum, such as a `limit` of 101       |

Some errors have headers:

- `401` has `WWW-Authenticate: Bearer`.
- `429` has `Retry-After`, with the seconds until the client can make requests again.
- `405` has `Allow`, which has the methods of only one of the endpoints of the path, such as `POST` for `PUT /api/v1/shorturls`.

## Rate limit

Each IP address can make up to 60 requests in each window of 60 seconds, by default, set by `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW` (see [Configuration](configuration.md#the-api)). Over it, a request gets `429` with `too_many_requests` and `Retry-After`.

- Every endpoint counts, and the counts add up: the requests of an address to any endpoint share its limit. The health check doesn't count, nor a path that no route has, nor a request whose body isn't valid JSON. A request whose values are wrong counts.
- The window is one for every address, and starts with the first request after the previous one ended. When it ends, every count starts again from 0, so an address can make up to twice its limit in a short time, at the end of one window and the start of the next.
- Each process of the API counts on its own, and forgets the counts when it restarts. With more than one process, an address can make up to the limit in each one (see [Running](running.md#more-than-one-process)).
- The address is the one of the connection. Behind a proxy, it is the address of the proxy, unless the service trusts it (see [Running](running.md#behind-a-proxy)).

## What the API doesn't do

- **CORS:** the API answers no CORS headers, so a web page of another origin can't call it from the browser, such as with `fetch`. CORS only applies to those calls, and not to navigations, such as following a short link and its redirect. The API is meant to be called by the servers of the systems that use the shortener, and the redirect to be followed by the browser of the user, so neither needs CORS. An application in the browser that calls the API directly, from another origin, would need it, with the origins it allows.
- **Its documentation:** the API doesn't serve its OpenAPI schema, nor a page of documentation: `/openapi.json`, `/docs` and `/redoc` answer `404`. The schema is [openapi.yaml](openapi.yaml), in the repository.

## Known limitations

- A user who was deleted can still create short URLs with an access token issued before the deletion, until it expires, and those short URLs are never deleted ([issue 0024](../issues/0024-a-deleted-user-can-create-short-urls-until-their-token-expires.md)).
- The short URLs of a deleted user keep resolving until the service processes the [event](events.md) of the deletion. That is accepted, since it doesn't harm the shortener (see [Owner](../architecture/domain.md#owner)).
- When the connection to the database is lost during the commit of a change, the service can't know whether the change was made, and answers `503`. Trying again may make it twice, such as creating two short URLs, or counting a resolution twice ([issue 0018](../issues/0018-a-commit-whose-result-is-unknown-is-answered-as-unavailable.md)).
