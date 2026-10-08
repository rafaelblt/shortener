# Domain

The domain is the core of the shortener: the rules that hold regardless of database, HTTP or framework. It lives in `shortener/domain/` and imports nothing from the other layers. It doesn't define the repository: its interface belongs to the layer that uses it.

This document describes the domain as it is in the code. Verified bugs that aren't fixed yet are [issues](issues/README.md) labeled `domain`, linked from where this document describes the code they affect. Decisions still to be made are in [Open questions](#open-questions).

## Overview

There is a single central concept: the **short URL**, a short slug that points to a target URL and belongs to an owner.

```
shortener/domain/
├── shorturl/
│   ├── shorturl.py        ShortURL
│   ├── shorturl_id.py     ShortURLID
│   ├── owner_id.py        OwnerID
│   ├── slug.py            Slug
│   ├── target_url.py      TargetURL
│   ├── status.py          ShortURLStatus
│   └── exceptions.py      the errors of ShortURL
└── shared/                code that doesn't depend on shorturl/
    ├── entity_id.py       EntityID
    ├── result.py          Result, Ok and Err
    ├── validation.py      StringValidation, ValidationError, ValidationIssue and IssueCode
    └── parsing.py         require_non_empty_string()
```

## Time

No rule of the domain reads the clock. Every operation that depends on the current moment receives it as a `now` argument: `ShortURL.create()`, `resolve()`, `is_expired()` and `is_available()`. This keeps the domain deterministic and leaves the source of time to the use cases.

- `create()` and `resolve()` store `now`, as `created_at` and `last_accessed_at`, so they check it: a `now` that isn't a `datetime`, `None` included, raises `ShortURLAttributeTypeError`. `resolve()` checks it before the availability, so it raises even when the short URL isn't available.
- `is_expired()` and `is_available()` don't check `now`. `is_expired()` compares it with `expires_at` when there is one, and `is_available()` and `resolve()` call `is_expired()` only in the `ACTIVE` status. Python can't compare a naive datetime with a timezone-aware one, so if only one of them is naive, the comparison raises `TypeError`.

The domain only deals with moments in time, not with timezones. It accepts datetimes in any timezone, naive ones included, and doesn't convert them: guaranteeing they are in UTC is up to the layer that provides them.

The clock is read in one place: `ShortURLID.generate()`, since a UUIDv7 contains the moment it was generated. No rule depends on that moment.

## Value objects

`Slug` and `TargetURL` are `str` subclasses whose value the domain validates. They offer three ways of getting an instance, each for a different situation:

| Way             | Checks                                                                                  | When a check fails                                                     | For                                                                                                  |
| --------------- | --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `create(value)` | Every rule of the value object                                                          | Returns `Err` with a `ValidationError`                                 | New values, such as a slug sent by a client. It is the recommended way.                              |
| The constructor | The same rules, by calling `create()`                                                   | Raises `ValueError`, whose only argument is the `ValidationError`      | Values known to be valid, such as literals in tests.                                                 |
| `parse(value)`  | Only that the value is a non-empty `str`, with [`require_non_empty_string()`](#parsing) | Raises `TypeError` if it isn't a `str`, and `ValueError` if it's empty | Values that already exist, such as one loaded from the database, or one used to look up a short URL. |

`create()` checks the rules with [`StringValidation`](#validation), and returns a [`Result`](#result): `Ok` with the instance, or `Err` with a `ValidationError` that has an issue for each rule the value breaks. Each issue has a code, and the codes are shared by the value objects, so the upper layers handle a `TOO_LONG` the same way, whichever value object returned it. A value that isn't a `str` only gets the `INVALID_TYPE` issue. The rules of each value object are in its section: [Slug](#slug) and [TargetURL](#targeturl).

The rules of `create()` can change, and a value accepted under older rules has to keep working. That is why `parse()` doesn't apply them, and only checks what any value of the type has.

`ShortURLID`, `OwnerID` and `ShortURLStatus` don't follow this model: see [IDs](#ids) and [Status](#status).

## ShortURL

`shorturl/shorturl.py`

| Field              | Type               | Rule                                                     |
| ------------------ | ------------------ | -------------------------------------------------------- |
| `id`               | `ShortURLID`       | Identity. See [IDs](#ids).                               |
| `slug`             | `Slug`             | The short path. See [Slug](#slug).                       |
| `target_url`       | `TargetURL`        | The destination. See [TargetURL](#targeturl).            |
| `owner_id`         | `OwnerID`          | Reference to the owner. See [Owner](#owner).             |
| `status`           | `ShortURLStatus`   | `create()` sets it to `ACTIVE`. See [Status](#status).   |
| `visit_count`      | `int`              | Number of visits, `>= 0`. `create()` sets it to `0`.     |
| `created_at`       | `datetime`         | `create()` sets it to `now`.                             |
| `expires_at`       | `datetime \| None` | `None` means it never expires.                           |
| `last_accessed_at` | `datetime \| None` | `create()` sets it to `None`, `resolve()` to `now`.      |

The fields are read-only properties, and change only through the [methods](#methods).

### Creating and restoring

`ShortURL.create(slug, target_url, owner_id, now, expires_at=None)` creates a new short URL: it generates the ID with `ShortURLID.generate()`, sets `created_at` to `now`, `status` to `ACTIVE`, `visit_count` to `0` and `last_accessed_at` to `None`.

`ShortURL.restore(*, id, slug, target_url, owner_id, status, visit_count, created_at, expires_at, last_accessed_at)` rebuilds a short URL that already exists, such as one loaded from the database. It takes every field, only by keyword, and keeps them as given.

Both call the constructor, which takes every field, with no defaults. It checks them in the order of the table, and raises at the first invalid one:

- a value whose type isn't the one in the table raises `ShortURLAttributeTypeError`. The check uses `isinstance`, so subclasses pass, including `bool` for `visit_count`;
- a negative `visit_count` raises `ValueError`.

Each field is checked on its own and never compared with another, so `expires_at` can be earlier than `created_at`.

`restore()` repeats the parameters of the constructor on purpose. The constructor may come to take values that only the domain should set, and restoring through its own method keeps the code that loads short URLs from setting them.

### Methods

| Method                                                       | Effect                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `resolve(now)`                                               | Checks `now` like the constructor checks `created_at`. When `is_available(now)` is true, records a visit: adds 1 to `visit_count` and sets `last_accessed_at` to `now`. Then returns `target_url`. Otherwise, raises the error in the [Status](#status) table and records nothing. |
| `is_expired(now)`                                            | `True` when `expires_at` isn't `None` and `expires_at <= now`. Doesn't look at `status`. See [Expiration](#expiration).                                                                                                                                                            |
| `is_available(now)`                                          | `True` when `status` is `ACTIVE` and `is_expired(now)` is false.                                                                                                                                                                                                                   |
| `enable()`                                                   | Sets `status` to `ACTIVE`. See [Status](#status).                                                                                                                                                                                                                                  |
| `disable()`                                                  | Sets `status` to `DEACTIVATED`. See [Status](#status).                                                                                                                                                                                                                             |
| `change_slug(new_slug)`, `change_target_url(new_target_url)` | Check the type of the new value like the constructor, and replace the field. `change_slug()` doesn't check that the slug is unique.                                                                                                                                                |

Recording the visit is part of `resolve()`, and not a method of its own, so that the domain decides when a visit counts: only when the short URL is available. The use cases can't forget to record it, or record it for a short URL that isn't available.

### IDs

`shorturl/shorturl_id.py` and `shorturl/owner_id.py`

`ShortURLID` and `OwnerID` are [`EntityID`s](#entityid). Two IDs are only equal when they have the same type and value, so a `ShortURLID` never equals an `OwnerID`.

- `ShortURLID.generate()` returns a new `ShortURLID` with a UUIDv7, from the `uuid6` package. UUIDv7 values are ordered by creation time, which suits database indexes better than random UUIDs.
- The ID of a short URL is generated by the domain, in `ShortURL.create()`: it exists from the moment the short URL is created, and is never generated by the database.
- `OwnerID` adds nothing to `EntityID`, and has no `generate()`: owners are created outside the service (see [Owner](#owner)).

### Owner

Every short URL has an owner: **there are no anonymous short URLs**.

The owner is only a reference. The domain stores the owner's identifier, but knows nothing about the user: there is no user entity, and no name, email, password or status. That is also why the domain doesn't check whether the owner exists.

`owner_id` is set when the short URL is created or restored, and no method changes it.

Two things happen outside the domain, but shape this rule:

- The owner's identity comes from a JWT validated in the upper layers, whose subject is the owner's UUID. The client never provides the owner directly.
- When a user is deleted, an external event will trigger the deletion of their short URLs. Until the event is processed, those short URLs keep working with an owner that no longer exists. This window is accepted because it doesn't harm the shortener.

### Slug

`shorturl/slug.py`

The slug is the short path that identifies the short URL. It is a [value object](#value-objects), and these are the rules of `Slug.create()`, in the order of its issues:

| Rule                                                                                                 | Issue code       |
| ---------------------------------------------------------------------------------------------------- | ---------------- |
| The whole value matches `SLUG_PATTERN`, `^[a-zA-Z0-9_-]+$`: only ASCII letters, digits, `_` and `-` | `INVALID_FORMAT` |
| At least `SLUG_MIN_LENGTH` (3) characters                                                            | `TOO_SHORT`      |
| At most `SLUG_MAX_LENGTH` (30) characters                                                            | `TOO_LONG`       |

An empty string breaks two rules, and gets `INVALID_FORMAT` and `TOO_SHORT`.

`Slug.generate()` picks `RANDOM_SLUG_LENGTH` (6) characters from `RANDOM_SLUG_CHARS`, the ASCII letters and digits, with `random.choices`, and returns them as a `Slug` built by the constructor. The length is within the limits and every character matches `SLUG_PATTERN`, so the slug always follows the rules of `create()`, and the constructor never raises.

Slugs are unique, but `Slug` and `ShortURL` don't check it.

### TargetURL

`shorturl/target_url.py`

The destination of the short URL. It is a [value object](#value-objects), and `TargetURL.create()` has a single rule: the value parses with `urllib.parse.urlparse`, its scheme is `https`, and its netloc (the host part) isn't empty. A value that breaks it gets `INVALID_FORMAT`, such as:

- one that `urlparse` fails to parse with `ValueError`, as `https://[invalid`;
- one whose scheme isn't `https`. `urlparse` lowercases the scheme, so `HTTPS://example.com` is accepted;
- one whose netloc is empty, as `https://` or `https:///path`.

Nothing else is checked: the netloc isn't validated, so `https://exa mple.com` is accepted.

### Status

`shorturl/status.py`

`ShortURLStatus` is an `Enum` whose values are the names in lowercase, such as `ACTIVE = "active"`.

| Status        | How it is reached                            |
| ------------- | -------------------------------------------- |
| `ACTIVE`      | `create()`, or `enable()` from `DEACTIVATED` |
| `DEACTIVATED` | `disable()` from `ACTIVE`                    |

What each method does in each status. Error names mean the method raises that error.

| Status        | `resolve(now)`                                                                                  | `enable()`          | `disable()`              |
| ------------- | ----------------------------------------------------------------------------------------------- | ------------------- | ------------------------ |
| `ACTIVE`      | Records a visit and returns `target_url`, or raises `ShortURLExpiredError` if `is_expired(now)` | Nothing             | Changes to `DEACTIVATED` |
| `DEACTIVATED` | `ShortURLDeactivatedError`                                                                      | Changes to `ACTIVE` | Nothing                  |

`resolve()` only looks at `expires_at` in the `ACTIVE` status, and `enable()` and `disable()` never look at it.

### Expiration

A short URL with an `expires_at` expires once that moment is reached: `is_expired(now)` is true when `expires_at <= now`. From then on, `is_available(now)` is false and, if the status is `ACTIVE`, `resolve(now)` raises `ShortURLExpiredError`. The status doesn't change.

Expiration isn't a status, and has a different meaning: no status says that a short URL has expired, and knowing it always takes comparing `expires_at` with `now`. It is checked when the short URL is used, so it never depends on a status being updated in time.

## Shared

`shared/`

### EntityID

`shared/entity_id.py`

The identity of an entity: a frozen dataclass with one field, `value: UUID`.

- Creating one with a `value` that isn't a `UUID` raises `TypeError`.
- Equality and hashing come from the dataclass: two `EntityID`s are only equal when they are of the same class and have the same `value`.
- `str()` returns the UUID as a string.

### Result

`shared/result.py`

`Result[T, E]` is `Ok[T] | Err[E]`, modeled after Rust's `Result`: the outcome of an operation that can fail, returned instead of raising an exception. `Ok` holds the result in `value`, and `Err` holds the failure in `error`. Both are frozen dataclasses, so they compare by content and can be matched:

```python
match result:
    case Ok(value): ...
    case Err(error): ...
```

| Method          | On `Ok(value)`        | On `Err(error)`                                     |
| --------------- | --------------------- | --------------------------------------------------- |
| `map(function)` | `Ok(function(value))` | The same `Err`, without calling `function`          |
| `unwrap()`      | `value`               | Raises `ValueError`, whose only argument is `error` |

### Validation

`shared/validation.py`

`StringValidation(value)` validates a value with rules chained one after the other, and `result()` ends the chain:

```python
StringValidation(value).min_length(3).max_length(30).result()
```

Each rule records a `ValidationIssue` when the value breaks it, and the chain goes on, so every broken rule is recorded, in the order of the chain. A value that isn't a `str` gets an `INVALID_TYPE` issue when `StringValidation` is created, and every rule is skipped.

| Method                  | Records                                                                                  |
| ----------------------- | ---------------------------------------------------------------------------------------- |
| `min_length(length)`    | `TOO_SHORT` when `len(value) < length`                                                   |
| `max_length(length)`    | `TOO_LONG` when `len(value) > length`                                                    |
| `matches(pattern)`      | `INVALID_FORMAT` when `pattern.fullmatch(value)` is `None`: the whole value has to match |
| `satisfies(rule, code)` | `code` when `rule(value)` is false. It adds a rule the methods above don't cover.        |

`result()` returns `Ok(value)` when no issue was recorded. Otherwise, it returns `Err` with a `ValidationError`: a frozen dataclass whose `issues` holds the recorded `ValidationIssue`s, as a tuple. A `ValidationIssue` is a frozen dataclass with a single field, `code`, an `IssueCode`. The codes describe the kind of rule that was broken, not what was validated, so a code means the same thing wherever it comes from:

| `IssueCode`      | Value              | The value...                       |
| ---------------- | ------------------ | ---------------------------------- |
| `INVALID_TYPE`   | `"invalid_type"`   | isn't of the expected type         |
| `TOO_SHORT`      | `"too_short"`      | is shorter than the minimum length |
| `TOO_LONG`       | `"too_long"`       | is longer than the maximum length  |
| `INVALID_FORMAT` | `"invalid_format"` | doesn't have the expected format   |

### Parsing

`shared/parsing.py`

`require_non_empty_string(value, type_name)` returns `value` when it is a non-empty `str`. Otherwise, it raises `TypeError` if it isn't a `str`, or `ValueError` if it's empty, with `type_name` in the message.

## Errors

`shorturl/exceptions.py`

A value that breaks a rule of a value object isn't an exception: `create()` returns it as a [`ValidationError`](#validation).

### Availability errors

`ShortURLAvailabilityError` and its subclasses `ShortURLDeactivatedError` and `ShortURLExpiredError` mean the short URL exists but isn't available. They extend `Exception` and carry no message or code. Only `resolve()` raises them, and only the subclasses, as in the [Status](#status) table. Nothing raises `ShortURLAvailabilityError` itself.

### Programming errors

Wrong types or values given to the domain's code. They are programming errors, not client input errors.

- `ShortURLAttributeTypeError`, a `TypeError`: wrong type given to `ShortURL.create()`, `ShortURL.restore()`, a `change_*()` method or `resolve()`.
- `ValueError`: a negative `visit_count` given to `ShortURL.restore()`. Also a value that breaks a rule of `create()`, given to the constructor of `Slug` or `TargetURL`.
- `TypeError`: an `EntityID` created with a `value` that isn't a `UUID`. Also a `now` that can't be compared with `expires_at`, given to `is_expired()`, `is_available()` or `resolve()` (see [Time](#time)).

### Parsing errors

`parse()` of `Slug` and `TargetURL` raises `TypeError` for a value that isn't a `str`, and `ValueError` for an empty one. See [Value objects](#value-objects).

## Open questions

Decisions to make during this phase. There are none at the moment.
