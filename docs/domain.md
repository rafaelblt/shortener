# Domain

The domain is the core of the shortener: the rules that hold regardless of database, HTTP or framework. It lives in `shortener/domain/` and imports nothing from the other layers.

This document describes the domain the restructuring is aiming for, and points out where the current code still differs from it.

## Overview

There is a single central concept: the **short URL**, a short slug that points to an original URL and belongs to an owner.

```
shortener/domain/
├── shorturl/   the ShortURL entity, its fields, errors and repository
└── shared/     pieces used by more than one concept
```

## Time

The domain never reads the clock. Every operation that depends on the current moment receives it as a `now` argument, in UTC: `ShortURL.create()`, `record_visit()`, `is_expired()`, `is_available()` and `resolve()`. This keeps the domain deterministic and leaves the source of time to the use cases.

## ShortURL

`shorturl/shorturl.py`

| Field              | Type               | Rule                                                 |
| ------------------ | ------------------ | ---------------------------------------------------- |
| `id`               | `ShortURLID`       | Identity. See [IDs](#ids).                           |
| `slug`             | `Slug`             | The short path. See [Slug](#slug).                   |
| `original_url`     | `OriginalURL`      | The destination. See [OriginalURL](#originalurl).    |
| `owner_id`         | `OwnerID`          | Reference to the owner. See [Owner](#owner).         |
| `status`           | `ShortURLStatus`   | Starts as `ACTIVE`. See [Status](#status).           |
| `visit_count`      | `int`              | Number of visits, never negative. Starts at 0.       |
| `created_at`       | `datetime`         | In UTC. The `now` given to `ShortURL.create()`.      |
| `expires_at`       | `datetime \| None` | In UTC. `None` means it never expires.               |
| `last_accessed_at` | `datetime \| None` | In UTC. The `now` of the last visit.                 |

A new short URL is created with `ShortURL.create()`, which generates its ID. The constructor takes every field and is meant for rebuilding a short URL that already exists, such as one loaded from the database.

The constructor checks the type of every field (`ShortURLAttributeTypeError`) and rejects a negative `visit_count` and datetimes outside UTC (`ValueError`).

The fields are read-only, and changes go through the methods:

| Method                   | Effect                                                                                  |
| ------------------------ | --------------------------------------------------------------------------------------- |
| `resolve(now)`           | Returns the `original_url` if the short URL is available at `now`. Otherwise, raises the matching error. |
| `record_visit(now)`      | Adds a visit and sets `last_accessed_at` to `now`. Doesn't check availability.          |
| `is_expired(now)`        | Whether `expires_at` has been reached at `now`. See [Expiration](#expiration).          |
| `is_available(now)`      | Whether the status is `ACTIVE` and the short URL hasn't expired at `now`.               |
| `enable()` / `disable()` | Switch between `ACTIVE` and `DEACTIVATED`.                                              |
| `change_slug()`, `change_original_url()`, `change_owner_id()` | Replace the field, checking its type.              |

### IDs

`shorturl/fields/shorturl_id.py` and `shorturl/fields/owner_id.py`

`ShortURLID` and `OwnerID` are `EntityID`s (see [Shared](#shared)). Two IDs are only equal when they have the same type and value, so a `ShortURLID` never equals an `OwnerID`.

- `ShortURLID.generate()` creates a new ID from a UUIDv7. UUIDv7 values are ordered by creation time, which suits database indexes better than random UUIDs.
- The ID of a short URL belongs to the domain: it exists from the moment the short URL is created, and never comes from the database.
- An `OwnerID` is never generated here: owners are created outside the service (see [Owner](#owner)).

### Owner

Every short URL has an owner: **there are no anonymous short URLs**.

The owner is only a reference. The domain stores the owner's identifier, but knows nothing about the user: there is no user entity, and no name, email, password or status. That is also why the domain doesn't check whether the owner exists.

Two things happen outside the domain, but shape this rule:

- The owner's identity comes from a JWT validated in the upper layers, whose subject is the owner's UUID. The client never provides the owner directly.
- When a user is deleted, an external event will trigger the deletion of their short URLs. Until the event is processed, those short URLs keep working with an owner that no longer exists. This window is accepted because it doesn't harm the shortener.

### Slug

`shorturl/fields/slug.py`

The slug is the short path that identifies the short URL. A valid slug:

- uses only ASCII letters, digits, `_` and `-`;
- is 3 to 30 characters long;
- is not in `FORBIDDEN_SLUGS` (`api`, `docs`, `admin`, `login` and so on). The comparison ignores case.

`Slug.generate_random()` generates a random 6-character slug made of letters and digits.

Slugs are unique. `generate_unique_slug()` (in `shorturl/utils.py`) generates random slugs until it finds one that doesn't exist in the repository, and gives up after a maximum number of attempts by raising `RuntimeError`.

### OriginalURL

`shorturl/fields/url.py`

The destination URL must have a scheme and a host, and use `https`. `OriginalURL` extends `URL` (`shared/valueobjects/url.py`), which does the generic scheme and host validation.

### Status

`shorturl/fields/status.py`

| Status        | Meaning                | How it is reached                                          |
| ------------- | ---------------------- | ---------------------------------------------------------- |
| `ACTIVE`      | Available              | Default on creation, or `enable()` from `DEACTIVATED`      |
| `DEACTIVATED` | Turned off by the owner | `disable()` from `ACTIVE`                                 |
| `EXPIRED`     | Marked as expired      | Only through the constructor. Reaching `expires_at` doesn't change the status. |
| `SUSPENDED`   | Suspended              | Only through the constructor. No method leads to it.       |
| `BANNED`      | Banned                 | Only through the constructor. No method leads to it.       |

`enable()` on an `ACTIVE` short URL and `disable()` on a `DEACTIVATED` one do nothing. In the `EXPIRED`, `SUSPENDED` and `BANNED` statuses, both raise the matching error, and so does `resolve()`.

### Expiration

A short URL with an `expires_at` stops working once that moment is reached: `is_expired(now)` is true when `expires_at <= now`. From then on, `resolve(now)` raises `ShortURLExpiredError` and `is_available(now)` is false, even though the status is still `ACTIVE`.

Expiration is checked when the short URL is used, against the given `now`, so it never depends on a status being updated in time.

### Repository

`shorturl/repository.py`

`ShortURLRepository` is the persistence interface the domain defines and the infrastructure implements. Its methods are asynchronous: `add`, `update`, `get_all`, `get_by_id`, `get_by_slug`, `list_paginated`, `delete_by_id` and `exists_by_slug`.

## Shared

`shared/`

| Module                | Contents                                                                          |
| --------------------- | --------------------------------------------------------------------------------- |
| `entity_id.py`        | `EntityID`, the identity of an entity: an immutable UUID, compared by type and value |
| `valueobjects/url.py` | `URL`, a string validated to have a scheme and a host                             |
| `datetime_utils.py`   | `is_utc()` and `ensure_utc()`                                                     |
| `pagination.py`       | `PaginatedResult`, a page of results with total, offset and limit                 |
| `exceptions.py`       | `DomainError`, `ValidationError` and `MultiValidationError`                       |
| `validator.py`        | `Validator` and `MultiFieldValidator`                                             |

## Errors

| Error                                       | Meaning                                                                                        |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `ValidationError` and subclasses            | An input value is invalid. Carries `field`, `value` and a stable `code` the API can return to the client: `SLUG_INVALID`, `SLUG_FORBIDDEN`, `SLUG_TOO_SHORT`, `SLUG_TOO_LONG`, `SLUG_ALREADY_EXISTS`, `URL_INVALID`. |
| `ShortURLAvailabilityError` and subclasses  | The short URL exists but isn't available: `Deactivated`, `Expired`, `Suspended` or `Banned`.   |
| `ShortURLAttributeTypeError` and `ValueError` | Wrong type or value given to the constructor or a method. A programming error, not a client input error. |
| `ShortURLRepositoryError` and subclasses    | Persistence failures, raised by the repository implementations.                                |

## Known problems

Verified in the current code. Fixing them is part of this phase.

1. **The slug length error messages are swapped.** `ShortURLSlugTooLongError` says "must be at least 30" and `ShortURLSlugTooShortError` says "must be at most 3".
2. **`generate_unique_slug()` makes one attempt more** than `max_attempts`.
3. **`Slug` accepts values that aren't strings.** `Slug(12345)` silently becomes `"12345"`.
4. **Duplicated validation.** `URL` and `OriginalURL` repeat the same check in `__new__` and in `validate()`.

## Open questions

Decisions to make during this phase:

- **`SUSPENDED` and `BANNED`.** They are moderation statuses, and no domain method leads to them. Should they stay?
- **`EXPIRED`.** Expiration is now checked against `expires_at` when the short URL is used, so nothing sets this status anymore. Should it stay?
- **`change_owner_id()`.** Does it make sense to transfer a short URL to another owner?
- **Owner operations in the repository**, such as listing or deleting an owner's short URLs. They should come in when the use cases need them.
- **Abstractions to revisit for simplicity:** `DomainEntity` (`get_fields()` is only used in tests), `MultiFieldValidator` (unused and untested), `Validator`, `ShortURLValidator`, and the overlapping repository errors (`ShortURLNotFoundError`, `ShortURLNotFoundInDatabaseError`, `ShortURLDeletionNotFoundError`).
