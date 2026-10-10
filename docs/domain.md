# Domain

The domain is the core of the shortener: the rules that hold regardless of database, HTTP or framework. It lives in `shortener/domain/` and imports nothing from the other layers, only from [`shortener/shared/`](shared.md). It doesn't define the repository: its interface belongs to the layer that uses it.

This document describes the domain as it is in the code. Verified bugs that aren't fixed yet are [issues](issues/README.md) labeled `domain`, linked from where this document describes the code they affect. Decisions still to be made are in [Open questions](#open-questions).

## Overview

There is a single central concept: the **short URL**, a short slug that points to a target URL and belongs to an owner.

```
shortener/domain/
├── shorturl.py        ShortURL
├── entity_id.py       EntityID
├── shorturl_id.py     ShortURLID
├── user_id.py         UserID
├── slug.py            Slug
├── target_url.py      TargetURL
├── status.py          ShortURLStatus
└── errors.py          ShortURLDeactivatedError
```

## Time

No rule of the domain reads the clock. Every operation that depends on the current moment receives it as a `now` argument: `ShortURL.create()` and `resolve()`. This keeps the domain deterministic and leaves the source of time to the use cases.

Both store `now`, as `created_at` and `last_resolved_at`, so they check it: a `now` that isn't a `datetime`, `None` included, raises `TypeError`, and a naive one raises `ValueError`. `resolve()` checks it before the availability, so it raises even when the short URL isn't available.

The domain only deals with moments in time, not with timezones. It accepts timezone-aware datetimes in any timezone, and doesn't convert them: guaranteeing they are in UTC is up to the layer that provides them. Aware datetimes in different timezones are compared by the moment they represent.

A datetime is naive, as Python defines it, when its `utcoffset()` returns `None`: it has no `tzinfo`, or its `tzinfo` gives no offset. The domain rejects naive datetimes because they aren't moments in time: comparing one with an aware datetime is always unequal with `==`, and raises `TypeError` with `<`.

The clock is read in one place: `ShortURLID.generate()`, since a UUIDv7 contains the moment it was generated. No rule depends on that moment.

## Value objects

`Slug` and `TargetURL` are `str` subclasses whose value the domain validates. They offer three ways of getting an instance, each for a different situation:

| Way             | Checks                                                                                           | When a check fails                                                     | For                                                                                                  |
| --------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `create(value)` | Every rule of the value object                                                                   | Returns `Err` with a `ValidationError`                                 | New values, such as a slug sent by a client. It is the recommended way.                              |
| The constructor | The same rules, by calling `create()`                                                            | Raises `ValueError`, whose only argument is the `ValidationError`      | Values known to be valid, such as literals in tests.                                                 |
| `parse(value)`  | Only that the value is a non-empty `str`, with [`require_non_empty_string()`](shared.md#parsing) | Raises `TypeError` if it isn't a `str`, and `ValueError` if it's empty | Values that already exist, such as one loaded from the database, or one used to look up a short URL. |

`create()` checks the rules with [`StringValidation`](shared.md#validation), and returns a [`Result`](shared.md#result): `Ok` with the instance, or `Err` with a `ValidationError` that has an issue for each rule the value breaks. Each issue has a code, and the codes are shared by the value objects, so the upper layers handle a `TOO_LONG` the same way, whichever value object returned it. A value that isn't a `str` only gets the `INVALID_TYPE` issue. The rules of each value object are in its section: [Slug](#slug) and [TargetURL](#targeturl).

The rules of `create()` can change, and a value accepted under older rules has to keep working. That is why `parse()` doesn't apply them, and only checks what any value of the type has.

`ShortURLID`, `UserID` and `ShortURLStatus` don't follow this model: see [IDs](#ids) and [Status](#status).

## ShortURL

`shorturl.py`

| Field              | Type               | Rule                                                                          |
| ------------------ | ------------------ | ----------------------------------------------------------------------------- |
| `id`               | `ShortURLID`       | Identity. See [IDs](#ids).                                                    |
| `slug`             | `Slug`             | The short path. See [Slug](#slug).                                            |
| `target_url`       | `TargetURL`        | The destination. See [TargetURL](#targeturl).                                 |
| `owner_id`         | `UserID`           | Reference to the owner. See [Owner](#owner).                                  |
| `status`           | `ShortURLStatus`   | `create()` sets it to `ACTIVE`. See [Status](#status).                        |
| `resolution_count` | `int`              | Number of times `resolve()` returned `Ok`, `>= 0`. `create()` sets it to `0`. |
| `created_at`       | `datetime`         | `create()` sets it to `now`.                                                  |
| `last_resolved_at` | `datetime \| None` | `create()` sets it to `None`, `resolve()` to `now`.                           |

The fields are read-only properties, and change only through the [methods](#methods).

`resolution_count` and `last_resolved_at` are about resolutions, not visits: the domain knows when it returned the target URL, not whether the client opened it.

### Creating and restoring

`ShortURL.create(slug, target_url, owner_id, now)` creates a new short URL: it generates the ID with `ShortURLID.generate()`, sets `created_at` to `now`, `status` to `ACTIVE`, `resolution_count` to `0` and `last_resolved_at` to `None`.

`ShortURL.restore(*, id, slug, target_url, owner_id, status, resolution_count, created_at, last_resolved_at)` rebuilds a short URL that already exists, such as one loaded from the database. It takes every field, only by keyword, and keeps them as given.

Both call the constructor, which takes every field, with no defaults. It checks them in the order of the table, and raises at the first invalid one:

- a value whose type isn't the one in the table raises `TypeError`, with a message naming the field, the expected type and the type received. The check uses `isinstance`, so subclasses pass, including `bool` for `resolution_count`;
- a negative `resolution_count` raises `ValueError`;
- a naive `created_at` or `last_resolved_at` raises `ValueError`, with a message naming the field and the value. See [Time](#time).

Each field is checked on its own and never compared with another, so `last_resolved_at` can be earlier than `created_at`.

`restore()` repeats the parameters of the constructor on purpose. The constructor may come to take values that only the domain should set, and restoring through its own method keeps the code that loads short URLs from setting them.

### Methods

| Method                                                       | Effect                                                                                                                                                                                                                                                                                                                                                            |
| ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `resolve(now)`                                               | Raises `TypeError`, with [`check_parameter_type()`](shared.md#type-checks), when `now` isn't a `datetime`, and `ValueError`, naming `now` and the value, when it is [naive](#time). When the status is `ACTIVE`, counts the resolution: adds 1 to `resolution_count` and sets `last_resolved_at` to `now`. Then returns `Ok` with `target_url`. Otherwise, returns `Err` with the error in the [Status](#status) table and counts nothing. |
| `enable()`                                                   | Sets `status` to `ACTIVE`. See [Status](#status).                                                                                                                                                                                                                                                                                                                 |
| `disable()`                                                  | Sets `status` to `DEACTIVATED`. See [Status](#status).                                                                                                                                                                                                                                                                                                            |
| `change_slug(new_slug)`, `change_target_url(new_target_url)` | Check the type of the new value like the constructor checks the field, and replace it. `change_slug()` doesn't check that the slug is unique.                                                                                                                                                                                                                     |

Counting the resolution is part of `resolve()`, and not a method of its own, so that the domain decides when a resolution counts: only when the short URL is available. The use cases can't forget to count it, or count it for a short URL that isn't available.

### IDs

`entity_id.py`, `shorturl_id.py` and `user_id.py`

`EntityID` is the identity of an entity: a frozen dataclass with one field, `value: UUID`.

- Creating one with a `value` that isn't a `UUID` raises `TypeError`.
- Equality and hashing come from the dataclass: two `EntityID`s are only equal when they are of the same class and have the same `value`.
- `str()` returns the UUID as a string.

`ShortURLID` and `UserID` are `EntityID`s. Two IDs are only equal when they have the same type and value, so a `ShortURLID` never equals a `UserID`.

- `ShortURLID.generate()` returns a new `ShortURLID` with a UUIDv7, from the `uuid6` package. UUIDv7 values are ordered by creation time, which suits database indexes better than random UUIDs.
- The ID of a short URL is generated by the domain, in `ShortURL.create()`: it exists from the moment the short URL is created, and is never generated by the database.
- `UserID` adds nothing to `EntityID`, and has no `generate()`: users are created outside the service (see [Owner](#owner)).

### Owner

Every short URL has an owner: **there are no anonymous short URLs**.

The owner is only a reference. The domain stores the owner's identifier, a `UserID`, but knows nothing about the user: there is no user entity, and no name, email, password or status. That is also why the domain doesn't check whether the owner exists.

Being the owner is a role that a user has in relation to a short URL, not an identity of its own: the upper layers will also compare the ID of the user making a request with `owner_id`, to check whether that user owns the short URL. That is why the field is named after the role, `owner_id`, and its type after what the ID identifies, `UserID`.

`owner_id` is set when the short URL is created or restored, and no method changes it.

Two things happen outside the domain, but shape this rule:

- The owner's identity comes from a JWT validated in the upper layers, whose subject is the owner's UUID. The client never provides the owner directly.
- When a user is deleted, an external event will trigger the deletion of their short URLs. Until the event is processed, those short URLs keep working with an owner that no longer exists. This window is accepted because it doesn't harm the shortener.

### Slug

`slug.py`

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

`target_url.py`

The destination of the short URL. It is a [value object](#value-objects), and `TargetURL.create()` has a single rule: the value parses with `urllib.parse.urlparse`, its scheme is `https`, and its netloc (the host part) isn't empty. A value that breaks it gets `INVALID_FORMAT`, such as:

- one that `urlparse` fails to parse with `ValueError`, as `https://[invalid`;
- one whose scheme isn't `https`. `urlparse` lowercases the scheme, so `HTTPS://example.com` is accepted;
- one whose netloc is empty, as `https://` or `https:///path`.

Nothing else is checked: the netloc isn't validated, so `https://exa mple.com` is accepted.

### Status

`status.py`

`ShortURLStatus` is an `Enum` whose values are the names in lowercase, such as `ACTIVE = "active"`.

| Status        | How it is reached                            |
| ------------- | -------------------------------------------- |
| `ACTIVE`      | `create()`, or `enable()` from `DEACTIVATED` |
| `DEACTIVATED` | `disable()` from `ACTIVE`                    |

What each method does in each status.

| Status        | `resolve(now)`                                     | `enable()`          | `disable()`              |
| ------------- | -------------------------------------------------- | ------------------- | ------------------------ |
| `ACTIVE`      | Counts the resolution and returns `Ok(target_url)` | Nothing             | Changes to `DEACTIVATED` |
| `DEACTIVATED` | `Err(ShortURLDeactivatedError())`                  | Changes to `ACTIVE` | Nothing                  |

## Errors

`errors.py`

The errors the use cases have to handle aren't exceptions: the domain returns them in a [`Result`](shared.md#result), so the use cases handle them as values instead of catching them. They are a value that breaks a rule of a value object, which `create()` returns as a [`ValidationError`](shared.md#validation), and the [availability error](#availability-error). Only [programming errors](#programming-errors) and [parsing errors](#parsing-errors) are raised.

### Availability error

`ShortURLDeactivatedError` means the short URL exists but isn't available, because its status is `DEACTIVATED`. It is a frozen dataclass with no fields, so every instance is equal to every other, and it can be matched as `Err(ShortURLDeactivatedError())`. It isn't an exception. Only `resolve()` returns it, as in the [Status](#status) table.

### Programming errors

Wrong types or values given to the domain's code. They are programming errors, not client input errors.

- `TypeError`: wrong type given to `ShortURL.create()`, `ShortURL.restore()`, a `change_*()` method or `resolve()`. Also an `EntityID` created with a `value` that isn't a `UUID`.
- `ValueError`: a negative `resolution_count` given to `ShortURL.restore()`. Also a naive datetime given to `ShortURL.create()`, `ShortURL.restore()` or `resolve()`. Also a value that breaks a rule of `create()`, given to the constructor of `Slug` or `TargetURL`.

### Parsing errors

`parse()` of `Slug` and `TargetURL` raises `TypeError` for a value that isn't a `str`, and `ValueError` for an empty one. See [Value objects](#value-objects).

## Open questions

Decisions to make during this phase. There are none at the moment.
