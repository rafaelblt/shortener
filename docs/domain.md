# Domain

The domain is the core of the shortener: the rules that hold regardless of database, HTTP or framework. It lives in `shortener/domain/` and imports nothing from the other layers. It doesn't define the repository: its interface belongs to the layer that uses it.

This document describes the domain as it is in the code. Verified bugs that aren't fixed yet are [issues](issues/README.md) labeled `domain`, linked from where this document describes the code they affect. Decisions still to be made are in [Open questions](#open-questions).

## Overview

There is a single central concept: the **short URL**, a short slug that points to a target URL and belongs to an owner.

```
shortener/domain/
├── domain_entity.py       DomainEntity, the base class of ShortURL
├── shorturl/
│   ├── shorturl.py        ShortURL
│   ├── fields/            ShortURLID, OwnerID, Slug, TargetURL and ShortURLStatus
│   ├── exceptions.py      the errors of ShortURL and its fields
│   └── validator.py       ShortURLValidator
└── shared/                code that doesn't depend on shorturl/
    ├── entity_id.py       EntityID
    ├── datetime_utils.py  is_utc() and ensure_utc()
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
| `target_url`       | `TargetURL`        | The destination. See [TargetURL](#targeturl).               |
| `owner_id`         | `OwnerID`          | Reference to the owner. See [Owner](#owner).                |
| `status`           | `ShortURLStatus`   | Defaults to `ACTIVE`. See [Status](#status).                |
| `visit_count`      | `int`              | Number of visits, `>= 0`. Defaults to `0`.                  |
| `created_at`       | `datetime`         | UTC. `create()` sets it to `now`.                           |
| `expires_at`       | `datetime \| None` | UTC. Defaults to `None`, which means it never expires.      |
| `last_accessed_at` | `datetime \| None` | UTC. Defaults to `None`. `record_visit()` sets it to `now`. |

The fields are read-only properties, and change only through the [methods](#methods).

### Creating and rebuilding

`ShortURL.create(slug, target_url, owner_id, now, expires_at=None)` creates a new short URL: it generates the ID with `ShortURLID.generate()`, sets `created_at` to `now`, and leaves `status`, `visit_count` and `last_accessed_at` at their defaults.

The constructor takes every field and is meant for rebuilding a short URL that already exists, such as one loaded from the database. `id`, `slug`, `target_url`, `owner_id` and `created_at` are required, and the other fields have the defaults in the table.

The constructor validates the fields in the order of the table, each with a public static method `validate_<field>()`, and raises at the first invalid one:

- a value whose type isn't the one in the table raises `ShortURLAttributeTypeError`. The check uses `isinstance`, so subclasses pass, including `bool` for `visit_count`;
- a negative `visit_count` raises `ValueError`;
- a datetime that is naive, or whose UTC offset isn't zero, raises `ValueError` (see [`is_utc()`](#datetime-helpers)).

Each field is checked on its own and never compared with another, so `expires_at` can be earlier than `created_at`.

### Methods

| Method                                                                                        | Effect                                                                                                                                        |
| --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `resolve(now)`                                                                                | Returns `target_url` when `is_available(now)` is true. Otherwise, raises the error in the [Status](#status) table. Doesn't record a visit.    |
| `record_visit(now)`                                                                           | Validates `now` with `validate_last_accessed_at()`, adds 1 to `visit_count` and sets `last_accessed_at` to `now`. Doesn't check availability. |
| `is_expired(now)`                                                                             | `True` when `expires_at` isn't `None` and `expires_at <= now`. Doesn't look at `status`. See [Expiration](#expiration).                       |
| `is_available(now)`                                                                           | `True` when `status` is `ACTIVE` and `is_expired(now)` is false.                                                                              |
| `enable()`                                                                                    | Sets `status` to `ACTIVE`. See [Status](#status).                                                                                             |
| `disable()`                                                                                   | Sets `status` to `DEACTIVATED`. See [Status](#status).                                                                                        |
| `change_slug(new_slug)`, `change_target_url(new_target_url)`                                  | Validate the type with the field's `validate_<field>()` and replace the field. `change_slug()` doesn't check that the slug is unique.         |
| `get_fields()`                                                                                | Static. Returns the names of the nine fields, in the order of the table. Required by `DomainEntity`.                                          |

### IDs

`shorturl/fields/shorturl_id.py` and `shorturl/fields/owner_id.py`

`ShortURLID` and `OwnerID` are [`EntityID`s](#entityid). Two IDs are only equal when they have the same type and value, so a `ShortURLID` never equals an `OwnerID`.

- `ShortURLID.generate()` returns a new `ShortURLID` with a UUIDv7, from the `uuid6` package. UUIDv7 values are ordered by creation time, which suits database indexes better than random UUIDs.
- The ID of a short URL is generated by the domain, in `ShortURL.create()`: it exists from the moment the short URL is created, and is never generated by the database.
- `OwnerID` adds nothing to `EntityID`, and has no `generate()`: owners are created outside the service (see [Owner](#owner)).

### Owner

Every short URL has an owner: **there are no anonymous short URLs**.

The owner is only a reference. The domain stores the owner's identifier, but knows nothing about the user: there is no user entity, and no name, email, password or status. That is also why the domain doesn't check whether the owner exists.

`owner_id` is set when the short URL is created or rebuilt, and no method changes it.

Two things happen outside the domain, but shape this rule:

- The owner's identity comes from a JWT validated in the upper layers, whose subject is the owner's UUID. The client never provides the owner directly.
- When a user is deleted, an external event will trigger the deletion of their short URLs. Until the event is processed, those short URLs keep working with an owner that no longer exists. This window is accepted because it doesn't harm the shortener.

### Slug

`shorturl/fields/slug.py`

The slug is the short path that identifies the short URL. `Slug` is a `str` subclass. Creating one converts the value with `str()` ([issue 0003](issues/0003-value-objects-dont-check-the-value-is-a-string.md)) and validates it with `Slug.validate_slug()`, which runs these checks in order and raises at the first that fails:

| Check                                                                                                   | Error                        |
| ------------------------------------------------------------------------------------------------------- | ---------------------------- |
| Matches `SLUG_PATTERN`, `^[a-zA-Z0-9_-]+$`: only ASCII letters, digits, `_` and `-`, and at least one character. A trailing `\n` also passes ([issue 0005](issues/0005-slug-can-end-with-a-newline.md)) | `ShortURLInvalidSlugError`   |
| Its lowercase form isn't in `FORBIDDEN_SLUGS`                                                           | `ShortURLForbiddenSlugError` |
| At least `SLUG_MIN_LENGTH` (3) characters                                                               | `ShortURLSlugTooShortError`  |
| At most `SLUG_MAX_LENGTH` (30) characters                                                               | `ShortURLSlugTooLongError`   |

`FORBIDDEN_SLUGS` holds `about`, `admin`, `api`, `config`, `contact`, `dashboard`, `docs`, `help`, `login`, `logout`, `privacy`, `support` and `terms`.

Because the pattern is checked first, an empty string raises `ShortURLInvalidSlugError`, not `ShortURLSlugTooShortError`. `Slug.validate_slug(value)` can also be called on its own, and returns `None` for a valid value.

`Slug.generate_random(length=DEFAULT_RANDOM_SLUG_LENGTH, chars=DEFAULT_CHARS)` picks `length` characters from `chars` with `random.choices` and returns them as a `Slug`, so the result goes through the same validation and can raise its errors. By default, it picks 6 characters among the ASCII letters and digits.

Slugs are unique, but `Slug` and `ShortURL` don't check it, and nothing in the domain raises `ShortURLSlugAlreadyExistsError`.

### TargetURL

`shorturl/fields/target_url.py`

The destination of the short URL. `TargetURL` is a `str` subclass. Creating one validates the value with `TargetURL.validate_target_url()`, which parses it with `urllib.parse.urlparse` and raises `ShortURLInvalidURLError` when:

- `urlparse` fails with `ValueError` or `TypeError`, as it does for `https://[invalid`;
- the scheme isn't `https`. `urlparse` lowercases the scheme, so `HTTPS://example.com` also passes;
- the netloc (the host part) is empty, as in `https://` or `https:///path`.

Nothing else is checked: the netloc isn't validated, so `https://exa mple.com` is a valid `TargetURL`. A value that isn't a string can raise other errors, such as `AttributeError` for `TargetURL(123)` ([issue 0003](issues/0003-value-objects-dont-check-the-value-is-a-string.md)).

`TargetURL.validate_target_url(value)` can also be called on its own, and returns `None` for a valid value.

### Status

`shorturl/fields/status.py`

`ShortURLStatus` is an `Enum` whose values are the names in lowercase, such as `ACTIVE = "active"`.

| Status        | How it is reached                                                                   |
| ------------- | ----------------------------------------------------------------------------------- |
| `ACTIVE`      | Default of the constructor and of `create()`, or `enable()` from `DEACTIVATED`      |
| `DEACTIVATED` | `disable()` from `ACTIVE`                                                           |

What each method does in each status. Error names mean the method raises that error.

| Status        | `resolve(now)`                                                                   | `enable()`               | `disable()`              |
| ------------- | -------------------------------------------------------------------------------- | ------------------------ | ------------------------ |
| `ACTIVE`      | Returns `target_url`, or raises `ShortURLExpiredError` if `is_expired(now)`      | Nothing                  | Changes to `DEACTIVATED` |
| `DEACTIVATED` | `ShortURLDeactivatedError`                                                       | Changes to `ACTIVE`      | Nothing                  |

`resolve()` only looks at `expires_at` in the `ACTIVE` status, and `enable()` and `disable()` never look at it.

### Expiration

A short URL with an `expires_at` expires once that moment is reached: `is_expired(now)` is true when `expires_at <= now`. From then on, `is_available(now)` is false and, if the status is `ACTIVE`, `resolve(now)` raises `ShortURLExpiredError`. The status doesn't change.

Expiration isn't a status, and has a different meaning: no status says that a short URL has expired, and knowing it always takes comparing `expires_at` with `now`. It is checked when the short URL is used, so it never depends on a status being updated in time.

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

### Datetime helpers

`shared/datetime_utils.py`

- `is_utc(dt)`: `True` when `dt` is timezone-aware and its UTC offset at that moment is zero. So a zone like `Europe/London` passes in winter and fails in summer. `ShortURL` uses it to validate its datetimes.
- `ensure_utc(dt)`: when `dt` is naive, returns it with its `tzinfo` set to UTC, without converting the time. When `dt` is aware, returns it unchanged, even if it isn't in UTC. The domain doesn't use it.

### Validators

`shared/validator.py`

- `Validator`: abstract class with one abstract async method, `validate(value) -> None`.
- `MultiFieldValidator(validators_map)`: `validators_map` maps a field name to a list of `Validator`s. `validate(**kwargs)` runs, concurrently with `asyncio.gather`, the validators mapped to each keyword argument. Keywords that aren't in the map are ignored. If any validator raised a `ValidationError`, it raises `MultiValidationError` with every `ValidationError` raised; exceptions of other types are discarded. Otherwise, it returns `None`.

## Errors

`shared/exceptions.py` and `shorturl/exceptions.py`

### Validation errors

`DomainError(code, message)` stores `code` and `message`, and its text is `[<code>]: <message>`. `ValidationError(value, field, code, message)` extends it with the invalid `value` and the `field` it belongs to. The `code` is a stable identifier the API can return to the client.

| Error                            | `code`                | `field`        | Raised by                                         |
| -------------------------------- | --------------------- | -------------- | ------------------------------------------------- |
| `ShortURLInvalidURLError`        | `URL_INVALID`         | `target_url`   | `TargetURL()`, `TargetURL.validate_target_url()`  |
| `ShortURLInvalidSlugError`       | `SLUG_INVALID`        | `slug`         | `Slug()`, `Slug.validate_slug()`                  |
| `ShortURLForbiddenSlugError`     | `SLUG_FORBIDDEN`      | `slug`         | `Slug()`, `Slug.validate_slug()`                  |
| `ShortURLSlugTooShortError`      | `SLUG_TOO_SHORT`      | `slug`         | `Slug()`, `Slug.validate_slug()`                  |
| `ShortURLSlugTooLongError`       | `SLUG_TOO_LONG`       | `slug`         | `Slug()`, `Slug.validate_slug()`                  |
| `ShortURLSlugAlreadyExistsError` | `SLUG_ALREADY_EXISTS` | `slug`         | Nothing in the domain                             |

Each of them also stores the input under its own name (`url` or `slug`), and the length errors store the limit (`min_length` or `max_length`). The messages of the length errors are swapped ([issue 0001](issues/0001-slug-length-error-messages-are-swapped.md)). They extend `ShortURLValidationError`, which extends `ValidationError` and adds nothing.

`MultiValidationError(errors)` holds a list of `ValidationError`s in `errors`. It extends `Exception`, not `DomainError`, and is raised by `MultiFieldValidator.validate()`.

### Availability errors

`ShortURLAvailabilityError` and its subclasses `ShortURLDeactivatedError` and `ShortURLExpiredError` mean the short URL exists but isn't available. They extend `Exception` and carry no message or code. Only `resolve()` raises them, and only the subclasses, as in the [Status](#status) table. Nothing raises `ShortURLAvailabilityError` itself.

### Programming errors

Wrong types or values given to the domain's code. They are programming errors, not client input errors.

- `ShortURLAttributeTypeError`, a `TypeError`: wrong type given to the `ShortURL` constructor, a `change_*()` method or `record_visit()`.
- `ValueError`: a negative `visit_count`, or a datetime that isn't in UTC, given to the `ShortURL` constructor or `record_visit()`.
- `TypeError`: an `EntityID` created with a `value` that isn't a `UUID`.

## Open questions

Decisions to make during this phase:

- **Abstractions to revisit for simplicity:** `DomainEntity` (`get_fields()` is only used in tests), `MultiFieldValidator` (unused and untested), `Validator` and `ShortURLValidator`.
