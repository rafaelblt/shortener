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

## ShortURL

`shorturl/shorturl.py`

| Field              | Type               | Rule                                                 |
| ------------------ | ------------------ | ---------------------------------------------------- |
| `pk`               | `PrimaryKey`       | Identity. Undefined until the short URL is persisted. |
| `slug`             | `Slug`             | The short path. See [Slug](#slug).                   |
| `original_url`     | `OriginalURL`      | The destination. See [OriginalURL](#originalurl).    |
| `owner_pk`         | `PrimaryKey`       | Reference to the owner. See [Owner](#owner).         |
| `status`           | `ShortURLStatus`   | Starts as `ACTIVE`. See [Status](#status).           |
| `visit_count`      | `int`              | Number of visits, never negative. Starts at 0.       |
| `created_at`       | `datetime`         | In UTC. Defaults to the moment of creation.          |
| `expires_at`       | `datetime \| None` | In UTC. `None` means it never expires.               |
| `last_accessed_at` | `datetime \| None` | In UTC. Moment of the last visit.                    |

The constructor checks the type of every field (`ShortURLAttributeTypeError`) and rejects a negative `visit_count` and datetimes outside UTC (`ValueError`).

The fields are read-only, and changes go through the methods:

| Method                   | Effect                                                                                  |
| ------------------------ | --------------------------------------------------------------------------------------- |
| `resolve()`              | Returns the `original_url` if the short URL is available. Otherwise, raises the status error. |
| `record_visit()`         | Adds a visit and updates `last_accessed_at`. Doesn't check the status.                  |
| `enable()` / `disable()` | Switch between `ACTIVE` and `DEACTIVATED`.                                              |
| `change_slug()`, `change_original_url()`, `change_owner_pk()` | Replace the field, checking its type.              |

The `is_available` property is `True` only when the status is `ACTIVE`.

### Owner

Every short URL has an owner: **there are no anonymous short URLs**.

The owner is only a reference. The domain stores the owner's identifier, but knows nothing about the user: there is no user entity, and no name, email, password or status. That is also why the domain doesn't check whether the owner exists.

Two things happen outside the domain, but shape this rule:

- The owner's identity comes from a JWT validated in the upper layers. The client never provides the owner directly.
- When a user is deleted, an external event will trigger the deletion of their short URLs. Until the event is processed, those short URLs keep working with an owner that no longer exists. This window is accepted because it doesn't harm the shortener.

> **Current divergence:** `owner_pk` is optional and, when omitted, stays undefined, which allows anonymous short URLs.

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
| `EXPIRED`     | Past `expires_at`      | On construction, if `expires_at` has already passed        |
| `SUSPENDED`   | Suspended              | Only through the constructor. No method leads to it.       |
| `BANNED`      | Banned                 | Only through the constructor. No method leads to it.       |

`enable()` on an `ACTIVE` short URL and `disable()` on a `DEACTIVATED` one do nothing. In the `EXPIRED`, `SUSPENDED` and `BANNED` statuses, both raise the matching error, and so does `resolve()`.

### Repository

`shorturl/repository.py`

`ShortURLRepository` is the persistence interface the domain defines and the infrastructure implements. Its methods are asynchronous: `add`, `update`, `get_all`, `get_by_pk`, `get_by_slug`, `list_paginated`, `delete_by_pk` and `exists_by_slug`.

## Shared

`shared/`

| Module                | Contents                                                                          |
| --------------------- | --------------------------------------------------------------------------------- |
| `primarykey.py`       | `PrimaryKey`, the identity of entities: an integer ID, or undefined until persisted |
| `valueobjects/url.py` | `URL`, a string validated to have a scheme and a host                             |
| `datetime_utils.py`   | `utc_now()`, `is_utc()` and `ensure_utc()`                                        |
| `pagination.py`       | `PaginatedResult`, a page of results with total, offset and limit                 |
| `exceptions.py`       | `DomainError`, `ValidationError` and `MultiValidationError`                       |
| `validator.py`        | `Validator` and `MultiFieldValidator`                                             |

## Errors

| Error                                       | Meaning                                                                                        |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `ValidationError` and subclasses            | An input value is invalid. Carries `field`, `value` and a stable `code` the API can return to the client: `SLUG_INVALID`, `SLUG_FORBIDDEN`, `SLUG_TOO_SHORT`, `SLUG_TOO_LONG`, `SLUG_ALREADY_EXISTS`, `URL_INVALID`. |
| `ShortURLAvailabilityError` and subclasses  | The short URL exists but isn't available: `Deactivated`, `Expired`, `Suspended` or `Banned`.   |
| `ShortURLAttributeTypeError` and `ValueError` | Wrong type or value given to the constructor. A programming error, not a client input error. |
| `ShortURLRepositoryError` and subclasses    | Persistence failures, raised by the repository implementations.                                |

## Known problems

Verified in the current code. Fixing them is part of this phase.

1. **Expiration is only evaluated on construction.** A short URL created with `expires_at` in the future stays `ACTIVE` after that moment passes, and `resolve()` keeps returning the URL.
2. **Anonymous short URLs are possible**, because `owner_pk` is optional (see [Owner](#owner)).
3. **The slug length error messages are swapped.** `ShortURLSlugTooLongError` says "must be at least 30" and `ShortURLSlugTooShortError` says "must be at most 3".
4. **`PrimaryKey.create_pk()` creates a key with no type.** Reading `pk_type` from it raises `AttributeError`.
5. **`generate_unique_slug()` makes one attempt more** than `max_attempts`.
6. **`Slug` accepts values that aren't strings.** `Slug(12345)` silently becomes `"12345"`.
7. **Duplicated validation.** `URL` and `OriginalURL` repeat the same check in `__new__` and in `validate()`.
8. **Inconsistency in `shorturl.py`.** It uses `datetime.now(tz=timezone.utc)` instead of `utc_now()`.
9. **Clock-dependent test.** `test_record_visit` compares times down to the second and can fail when a second ticks over.

## Open questions

Decisions to make during this phase:

- **`SUSPENDED` and `BANNED`.** They are moderation statuses, and no domain method leads to them. Should they stay?
- **Format of the owner reference.** It is currently an integer-ID `PrimaryKey`, but the identifier that comes from the JWT (`sub`) is a string. `PrimaryKey.create_pk()` seems to have started this change.
- **`change_owner_pk()`.** Does it make sense to transfer a short URL to another owner?
- **Owner operations in the repository**, such as listing or deleting an owner's short URLs. They should come in when the use cases need them.
- **Abstractions to revisit for simplicity:** `DomainEntity` (`get_fields()` is only used in tests), `MultiFieldValidator` (unused and untested), `Validator`, `ShortURLValidator`, and the overlapping repository errors (`ShortURLNotFoundError`, `ShortURLNotFoundInDatabaseError`, `ShortURLDeletionNotFoundError`, `ShortURLInvalidToUpdateError`).
