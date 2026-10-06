# Domain

The domain is the core of the shortener: the rules that hold regardless of database, HTTP or framework. It lives in `shortener/domain/` and imports nothing from the other layers.

This document describes the domain as it is in the code. Bugs that are verified but not fixed yet are in [Known problems](#known-problems), and decisions still to be made are in [Open questions](#open-questions).

## Overview

There is a single central concept: the **short URL**, a short slug that points to an original URL and belongs to an owner.

```
shortener/domain/
├── domain_entity.py       DomainEntity, the base class of ShortURL
├── shorturl/
│   ├── shorturl.py        ShortURL
│   ├── fields/            ShortURLID, OwnerID, Slug, OriginalURL and ShortURLStatus
│   ├── exceptions.py      the errors of ShortURL and its fields
│   ├── repository.py      ShortURLRepository
│   ├── validator.py       ShortURLValidator
│   └── utils.py           generate_unique_slug()
└── shared/                code that doesn't depend on shorturl/
    ├── entity_id.py       EntityID
    ├── valueobjects/      URL and InvalidURLError
    ├── datetime_utils.py  is_utc() and ensure_utc()
    ├── pagination.py      PaginatedResult
    ├── exceptions.py      DomainError, ValidationError and MultiValidationError
    └── validator.py       Validator and MultiFieldValidator
```

## Time

No rule of the domain reads the clock. Every operation that depends on the current moment receives it as a `now` argument: `ShortURL.create()`, `record_visit()`, `is_expired()`, `is_available()` and `resolve()`. This keeps the domain deterministic and leaves the source of time to the use cases.

- `create()` and `record_visit()` store `now`, as `created_at` and `last_accessed_at`, so they validate it like those fields: a `now` that isn't a timezone-aware UTC datetime raises `ShortURLAttributeTypeError` or `ValueError`.
- `is_expired()`, `is_available()` and `resolve()` don't validate `now`. `is_expired()` compares it with `expires_at` when there is one, and the other two call `is_expired()` only in the `ACTIVE` status. In that comparison, a `now` that isn't a timezone-aware datetime raises `TypeError`.

The clock is read in one place: `ShortURLID.generate()`, since a UUIDv7 contains the moment it was generated. No rule depends on that moment.

## DomainEntity

`domain_entity.py`

Abstract base class of entities. A subclass implements:

- `get_fields()`: a static method that returns the names of the entity's fields;
- `id`: a property that returns the entity's `EntityID`.

`ShortURL` is its only subclass.

## ShortURL

`shorturl/shorturl.py`

| Field              | Type               | Rule                                                        |
| ------------------ | ------------------ | ----------------------------------------------------------- |
| `id`               | `ShortURLID`       | Identity. See [IDs](#ids).                                  |
| `slug`             | `Slug`             | The short path. See [Slug](#slug).                          |
| `original_url`     | `OriginalURL`      | The destination. See [OriginalURL](#originalurl).           |
| `owner_id`         | `OwnerID`          | Reference to the owner. See [Owner](#owner).                |
| `status`           | `ShortURLStatus`   | Defaults to `ACTIVE`. See [Status](#status).                |
| `visit_count`      | `int`              | Number of visits, `>= 0`. Defaults to `0`.                  |
| `created_at`       | `datetime`         | UTC. `create()` sets it to `now`.                           |
| `expires_at`       | `datetime \| None` | UTC. Defaults to `None`, which means it never expires.      |
| `last_accessed_at` | `datetime \| None` | UTC. Defaults to `None`. `record_visit()` sets it to `now`. |

The fields are read-only properties, and change only through the [methods](#methods).

### Creating and rebuilding

`ShortURL.create(slug, original_url, owner_id, now, expires_at=None)` creates a new short URL: it generates the ID with `ShortURLID.generate()`, sets `created_at` to `now`, and leaves `status`, `visit_count` and `last_accessed_at` at their defaults.

The constructor takes every field and is meant for rebuilding a short URL that already exists, such as one loaded from the database. `id`, `slug`, `original_url`, `owner_id` and `created_at` are required, and the other fields have the defaults in the table.

The constructor validates the fields in the order of the table, each with a public static method `validate_<field>()`, and raises at the first invalid one:

- a value whose type isn't the one in the table raises `ShortURLAttributeTypeError`. The check uses `isinstance`, so subclasses pass, including `bool` for `visit_count`;
- a negative `visit_count` raises `ValueError`;
- a datetime that is naive, or whose UTC offset isn't zero, raises `ValueError` (see [`is_utc()`](#datetime-helpers)).

Each field is checked on its own and never compared with another, so `expires_at` can be earlier than `created_at`.

### Methods

| Method                                                                                   | Effect                                                                                                                                       |
| ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `resolve(now)`                                                                           | Returns `original_url` when `is_available(now)` is true. Otherwise, raises the error in the [Status](#status) table. Doesn't record a visit. |
| `record_visit(now)`                                                                      | Validates `now` with `validate_last_accessed_at()`, adds 1 to `visit_count` and sets `last_accessed_at` to `now`. Doesn't check availability. |
| `is_expired(now)`                                                                        | `True` when `expires_at` isn't `None` and `expires_at <= now`. Doesn't look at `status`. See [Expiration](#expiration).                      |
| `is_available(now)`                                                                      | `True` when `status` is `ACTIVE` and `is_expired(now)` is false.                                                                             |
| `enable()`                                                                               | Changes `DEACTIVATED` to `ACTIVE`. See [Status](#status).                                                                                    |
| `disable()`                                                                              | Changes `ACTIVE` to `DEACTIVATED`. See [Status](#status).                                                                                    |
| `change_slug(new_slug)`, `change_original_url(new_url)`, `change_owner_id(new_owner_id)` | Validate the type with the field's `validate_<field>()` and replace the field. `change_slug()` doesn't check that the slug is unique.         |
| `get_fields()`                                                                           | Static. Returns the names of the nine fields, in the order of the table. Required by `DomainEntity`.                                         |

### IDs

`shorturl/fields/shorturl_id.py` and `shorturl/fields/owner_id.py`

`ShortURLID` and `OwnerID` are [`EntityID`s](#entityid). Two IDs are only equal when they have the same type and value, so a `ShortURLID` never equals an `OwnerID`.

- `ShortURLID.generate()` returns a new `ShortURLID` with a UUIDv7, from the `uuid6` package. UUIDv7 values are ordered by creation time, which suits database indexes better than random UUIDs.
- The ID of a short URL is generated by the domain, in `ShortURL.create()`: it exists from the moment the short URL is created, and is never generated by the database.
- `OwnerID` adds nothing to `EntityID`, and has no `generate()`: owners are created outside the service (see [Owner](#owner)).

### Owner

Every short URL has an owner: **there are no anonymous short URLs**.

The owner is only a reference. The domain stores the owner's identifier, but knows nothing about the user: there is no user entity, and no name, email, password or status. That is also why the domain doesn't check whether the owner exists.

Two things happen outside the domain, but shape this rule:

- The owner's identity comes from a JWT validated in the upper layers, whose subject is the owner's UUID. The client never provides the owner directly.
- When a user is deleted, an external event will trigger the deletion of their short URLs. Until the event is processed, those short URLs keep working with an owner that no longer exists. This window is accepted because it doesn't harm the shortener.

### Slug

`shorturl/fields/slug.py`

The slug is the short path that identifies the short URL. `Slug` is a `str` subclass. Creating one converts the value with `str()` (see [Known problems](#known-problems)) and validates it with `Slug.validate_slug()`, which runs these checks in order and raises at the first that fails:

| Check                                                                                                   | Error                        |
| ------------------------------------------------------------------------------------------------------- | ---------------------------- |
| Matches `SLUG_PATTERN`, `^[a-zA-Z0-9_-]+$`: only ASCII letters, digits, `_` and `-`, and at least one character | `ShortURLInvalidSlugError`   |
| Its lowercase form isn't in `FORBIDDEN_SLUGS`                                                           | `ShortURLForbiddenSlugError` |
| At least `SLUG_MIN_LENGTH` (3) characters                                                               | `ShortURLSlugTooShortError`  |
| At most `SLUG_MAX_LENGTH` (30) characters                                                               | `ShortURLSlugTooLongError`   |

`FORBIDDEN_SLUGS` holds `about`, `admin`, `api`, `config`, `contact`, `dashboard`, `docs`, `help`, `login`, `logout`, `privacy`, `support` and `terms`.

Because the pattern is checked first, an empty string raises `ShortURLInvalidSlugError`, not `ShortURLSlugTooShortError`. `Slug.validate_slug(value)` can also be called on its own, and returns `None` for a valid value.

`Slug.generate_random(length=DEFAULT_RANDOM_SLUG_LENGTH, chars=DEFAULT_CHARS)` picks `length` characters from `chars` with `random.choices` and returns them as a `Slug`, so the result goes through the same validation. By default, it picks 6 characters among the ASCII letters and digits.

Slugs are unique, but `Slug` and `ShortURL` don't check it, and nothing in the domain raises `ShortURLSlugAlreadyExistsError`. `generate_unique_slug(repository, length=DEFAULT_RANDOM_SLUG_LENGTH, max_attempts=DEFAULT_MAX_ATTEMPS_TO_GENERATE_UNIQUE_SLUG)`, in `shorturl/utils.py`, calls `Slug.generate_random(length)` until `repository.exists_by_slug()` returns `False` for the generated slug, and returns that slug. If no attempt succeeds, it raises `RuntimeError` (see [Known problems](#known-problems)). `max_attempts` defaults to 100.

### OriginalURL

`shorturl/fields/url.py`

The destination of the short URL. `OriginalURL` extends [`URL`](#url), so the value must have a scheme and a netloc, and adds one rule: the scheme must be `https`. Any failure raises `ShortURLInvalidURLError`, including the `InvalidURLError` raised by `URL`, which is converted into it.

`OriginalURL.validate(value)` runs the same checks without creating an `OriginalURL` (see [Known problems](#known-problems)).

### Status

`shorturl/fields/status.py`

`ShortURLStatus` is an `Enum` whose values are the names in lowercase, such as `ACTIVE = "active"`.

| Status        | How it is reached                                                                   |
| ------------- | ----------------------------------------------------------------------------------- |
| `ACTIVE`      | Default of the constructor and of `create()`, or `enable()` from `DEACTIVATED`      |
| `DEACTIVATED` | `disable()` from `ACTIVE`                                                           |
| `EXPIRED`     | Only by passing it to the constructor. Reaching `expires_at` doesn't change the status. |
| `SUSPENDED`   | Only by passing it to the constructor                                               |
| `BANNED`      | Only by passing it to the constructor                                               |

What each method does in each status. Error names mean the method raises that error.

| Status        | `resolve(now)`                                                                   | `enable()`               | `disable()`              |
| ------------- | -------------------------------------------------------------------------------- | ------------------------ | ------------------------ |
| `ACTIVE`      | Returns `original_url`, or raises `ShortURLExpiredError` if `is_expired(now)`    | Nothing                  | Changes to `DEACTIVATED` |
| `DEACTIVATED` | `ShortURLDeactivatedError`                                                       | Changes to `ACTIVE`      | Nothing                  |
| `EXPIRED`     | `ShortURLExpiredError`                                                           | `ShortURLExpiredError`   | `ShortURLExpiredError`   |
| `SUSPENDED`   | `ShortURLSuspendedError`                                                         | `ShortURLSuspendedError` | `ShortURLSuspendedError` |
| `BANNED`      | `ShortURLBannedError`                                                            | `ShortURLBannedError`    | `ShortURLBannedError`    |

`resolve()` only looks at `expires_at` in the `ACTIVE` status, and `enable()` and `disable()` never look at it.

### Expiration

A short URL with an `expires_at` expires once that moment is reached: `is_expired(now)` is true when `expires_at <= now`. From then on, `is_available(now)` is false and, if the status is `ACTIVE`, `resolve(now)` raises `ShortURLExpiredError`. The status doesn't change.

Expiration is checked when the short URL is used, against the given `now`, so it never depends on a status being updated in time.

`is_expired()` only looks at `expires_at`. A short URL in the `EXPIRED` status with no `expires_at`, or with one later than `now`, has `is_expired(now)` false. It is still unavailable, because its status isn't `ACTIVE`.

### Repository

`shorturl/repository.py`

`ShortURLRepository` is the persistence interface the domain defines and the infrastructure implements. Its methods are abstract and asynchronous, and their docstrings define the contract:

| Method                          | Returns                     | Contract                                                                          |
| ------------------------------- | --------------------------- | --------------------------------------------------------------------------------- |
| `add(shorturl)`                 | `ShortURL`                  | Stores the short URL and returns it.                                              |
| `update(shorturl)`              | `ShortURL`                  | Updates a stored short URL and returns it. Raises `ShortURLNotFoundError` if it isn't stored. |
| `get_all()`                     | `list[ShortURL]`            | Every stored short URL.                                                           |
| `get_by_id(id: ShortURLID)`     | `ShortURL \| None`          | The short URL with that ID, or `None`.                                            |
| `get_by_slug(slug: str)`        | `ShortURL \| None`          | The short URL with that slug, or `None`.                                          |
| `list_paginated(offset, limit)` | `PaginatedResult[ShortURL]` | Up to `limit` short URLs, starting at `offset`.                                   |
| `delete_by_id(id: ShortURLID)`  | `ShortURL`                  | Deletes the short URL and returns it. Raises `ShortURLNotFoundError` if it isn't stored. |
| `exists_by_slug(slug: str)`     | `bool`                      | Whether a short URL with that slug is stored.                                     |

It also has two class attributes, `EntityType = ShortURL` and `exceptions = {"entity_not_found": ShortURLNotFoundError}`. Nothing in `shortener/` reads them, only the test mock `tests/fixtures/mocks/chameleon_repository.py`.

### ShortURLValidator

`shorturl/validator.py`

Abstract class with one abstract async method, `validate(shorturl) -> None`. Its docstring defines the contract: return `None` when the short URL is valid, and raise `ShortURLValidationError` when any part of it isn't. The domain has no implementation of it, and doesn't call it.

## Shared

`shared/`

### EntityID

`shared/entity_id.py`

The identity of an entity: a frozen dataclass with one field, `value: UUID`.

- Creating one with a `value` that isn't a `UUID` raises `TypeError`.
- Equality and hashing come from the dataclass: two `EntityID`s are only equal when they are of the same class and have the same `value`.
- `str()` returns the UUID as a string.

### URL

`shared/valueobjects/url.py`

`URL` is a `str` subclass. Creating one parses the value with `urllib.parse.urlparse`, and raises `InvalidURLError` when `urlparse` fails with `ValueError` or `TypeError`, or when the scheme or the netloc (the host part) is empty. Nothing else is checked: the netloc isn't validated, so `https://exa mple.com` is a valid `URL`.

- `is_https()`: whether the scheme is `https`. `urlparse` lowercases the scheme, so `HTTPS://example.com` also passes.
- `URL.validate(value)`: runs the same checks without creating a `URL`, and returns `None`.

### Datetime helpers

`shared/datetime_utils.py`

- `is_utc(dt)`: `True` when `dt` is timezone-aware and its UTC offset at that moment is zero. So a zone like `Europe/London` passes in winter and fails in summer. `ShortURL` uses it to validate its datetimes.
- `ensure_utc(dt)`: when `dt` is naive, returns it with its `tzinfo` set to UTC, without converting the time. When `dt` is aware, returns it unchanged, even if it isn't in UTC. The domain doesn't use it.

### PaginatedResult

`shared/pagination.py`

A page of items, generic on the item type: `PaginatedResult(items, total, offset, limit)`. The four arguments are stored as attributes with the same names, without validation. Derived properties:

| Property       | Value                     |
| -------------- | ------------------------- |
| `current_page` | `offset // limit + 1`     |
| `total_pages`  | `ceil(total / limit)`     |
| `has_next`     | `offset + limit < total`  |
| `has_previous` | `offset > 0`              |

With `limit = 0`, `current_page` and `total_pages` raise `ZeroDivisionError`.

### Validators

`shared/validator.py`

- `Validator`: abstract class with one abstract async method, `validate(value) -> None`.
- `MultiFieldValidator(validators_map)`: `validators_map` maps a field name to a list of `Validator`s. `validate(**kwargs)` runs, concurrently with `asyncio.gather`, the validators mapped to each keyword argument. Keywords that aren't in the map are ignored. If any validator raised a `ValidationError`, it raises `MultiValidationError` with every `ValidationError` raised; exceptions of other types are discarded. Otherwise, it returns `None`.

## Errors

`shared/exceptions.py`, `shared/valueobjects/url.py` and `shorturl/exceptions.py`

### Validation errors

`DomainError(code, message)` stores `code` and `message`, and its text is `[<code>]: <message>`. `ValidationError(value, field, code, message)` extends it with the invalid `value` and the `field` it belongs to. The `code` is a stable identifier the API can return to the client.

| Error                            | `code`                | `field`        | Raised by                                 |
| -------------------------------- | --------------------- | -------------- | ----------------------------------------- |
| `InvalidURLError`                | `INVALID_URL`         | `url`          | `URL()`, `URL.validate()`                 |
| `ShortURLInvalidURLError`        | `URL_INVALID`         | `original_url` | `OriginalURL()`, `OriginalURL.validate()` |
| `ShortURLInvalidSlugError`       | `SLUG_INVALID`        | `slug`         | `Slug()`, `Slug.validate_slug()`          |
| `ShortURLForbiddenSlugError`     | `SLUG_FORBIDDEN`      | `slug`         | `Slug()`, `Slug.validate_slug()`          |
| `ShortURLSlugTooShortError`      | `SLUG_TOO_SHORT`      | `slug`         | `Slug()`, `Slug.validate_slug()`          |
| `ShortURLSlugTooLongError`       | `SLUG_TOO_LONG`       | `slug`         | `Slug()`, `Slug.validate_slug()`          |
| `ShortURLSlugAlreadyExistsError` | `SLUG_ALREADY_EXISTS` | `slug`         | Nothing in the domain                     |

Each of them also stores the input under its own name (`url` or `slug`), and the length errors store the limit (`min_length` or `max_length`). `InvalidURLError` extends `ValidationError` directly. The others extend `ShortURLValidationError`, which extends `ValidationError` and adds nothing.

`MultiValidationError(errors)` holds a list of `ValidationError`s in `errors`. It extends `Exception`, not `DomainError`, and is raised by `MultiFieldValidator.validate()`.

### Availability errors

`ShortURLAvailabilityError` and its subclasses `ShortURLDeactivatedError`, `ShortURLExpiredError`, `ShortURLSuspendedError` and `ShortURLBannedError` mean the short URL exists but isn't available. They extend `Exception` and carry no message or code. `resolve()`, `enable()` and `disable()` raise the subclasses, as in the [Status](#status) table. `resolve()` raises `ShortURLAvailabilityError` itself only for a status it doesn't handle, which none of the current statuses is.

### Programming errors

Wrong types or values given to the domain's code. They are programming errors, not client input errors.

- `ShortURLAttributeTypeError`, a `TypeError`: wrong type given to the `ShortURL` constructor, a `change_*()` method or `record_visit()`.
- `ValueError`: a negative `visit_count`, or a datetime that isn't in UTC, given to the `ShortURL` constructor or `record_visit()`.
- `TypeError`: an `EntityID` created with a `value` that isn't a `UUID`.

### Repository errors

- `ShortURLRepositoryError` extends `Exception`, and has two subclasses:
  - `ShortURLNotFoundError(value, field)`: no short URL has `field` equal to `value`. The repository contract raises it from `update()` and `delete_by_id()`.
  - `ShortURLNotFoundInDatabaseError`: adds nothing to `ShortURLRepositoryError`. Nothing in the domain raises it.
- `ShortURLDeletionNotFoundError` extends `Exception` directly, not `ShortURLRepositoryError`. Nothing in the domain raises it.

### Other errors

- `RuntimeError`: raised by `generate_unique_slug()` when every attempt finds an existing slug.

## Known problems

Verified in the current code. Fixing them is part of this phase.

1. **The slug length error messages are swapped.** `ShortURLSlugTooLongError` says "must be at least 30" and `ShortURLSlugTooShortError` says "must be at most 3".
2. **`generate_unique_slug()` makes one attempt more** than `max_attempts`.
3. **Value objects don't check that the value is a string.** `Slug(12345)` silently becomes `"12345"`, and `URL(123)` and `OriginalURL(123)` raise `AttributeError` instead of a validation error.
4. **Duplicated validation.** `URL` and `OriginalURL` repeat the same check in `__new__` and in `validate()`.
5. **A slug can end with a newline.** `SLUG_PATTERN` ends in `$`, which `re.match` also matches before a trailing `\n`, so `Slug("abc\n")` is valid.
6. **`generate_unique_slug()` can raise `ShortURLForbiddenSlugError`.** `Slug.generate_random()` can produce a forbidden slug (with the default length of 6, `config` or `logout` in any letter case), and the error escapes instead of leading to a new attempt.

## Open questions

Decisions to make during this phase:

- **`SUSPENDED` and `BANNED`.** They are moderation statuses, and no domain method leads to them. Should they stay?
- **`EXPIRED`.** Expiration is now checked against `expires_at` when the short URL is used, so nothing sets this status anymore. Should it stay?
- **`change_owner_id()`.** Does it make sense to transfer a short URL to another owner?
- **Owner operations in the repository**, such as listing or deleting an owner's short URLs. They should come in when the use cases need them.
- **Abstractions to revisit for simplicity:** `DomainEntity` (`get_fields()` is only used in tests), `MultiFieldValidator` (unused and untested), `Validator`, `ShortURLValidator`, and the overlapping not-found errors (`ShortURLNotFoundError`, `ShortURLNotFoundInDatabaseError`, `ShortURLDeletionNotFoundError`).
