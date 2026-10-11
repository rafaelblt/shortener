# Use cases

The use cases orchestrate the [domain](domain.md) for each operation of the service. They live in `shortener/use_cases/`, and import only from the domain and from [`shortener/shared/`](shared.md). What they need from the other layers, such as storing short URLs or knowing who makes the request, they define as [abstractions](#abstractions), which the other layers implement.

This document describes the use cases as they are in the code. Verified bugs that aren't fixed yet are [issues](issues/README.md) labeled `use_cases`, linked from where this document describes the code they affect. Decisions still to be made are in [Open questions](#open-questions).

## Overview

```
shortener/use_cases/
├── shorturl_repository.py   ShortURLReader, ShortURLRepository and SlugTakenError
├── unit_of_work.py          UnitOfWork and Transaction
├── current_user.py          CurrentUser
├── clock.py                 Clock
├── errors.py                NotAuthenticatedError, ShortURLNotFoundError, InvalidInputError,
│                            FieldError and NothingToUpdateError
└── shorturl_details.py      ShortURLDetails
```

## Abstractions

The abstractions are `Protocol`s, so the other layers implement them without inheriting anything. The use cases receive the implementations in their constructors.

### Reading and writing

`shorturl_repository.py`

`ShortURLReader` reads short URLs:

| Method                    | Returns                                                                                        |
| ------------------------- | ---------------------------------------------------------------------------------------------- |
| `get_by_id(id)`           | The short URL whose `id` is the given `ShortURLID`, or `None` when there is none.             |
| `get_by_slug(slug)`       | The short URL whose `slug` is the given `Slug`, or `None` when there is none.                 |
| `list_by_owner(owner_id)` | A list of the short URLs whose `owner_id` is the given `UserID`, empty when there are none. The order isn't defined. |

`ShortURLRepository` is a `ShortURLReader` that also writes:

| Method             | Effect                                                                                                                      |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `add(shorturl)`    | Stores a new short URL. Returns `Ok(None)`, or `Err(SlugTakenError(slug))` when another short URL has its slug.           |
| `save(shorturl)`   | Stores every field of a short URL that is already stored, replacing what was there. Returns the same as `add()`.          |
| `remove(shorturl)` | Deletes a stored short URL. Returns `None`.                                                                               |

- `SlugTakenError` is a frozen dataclass with the `slug` that is taken.
- The uniqueness of the slug is checked when `add()` or `save()` writes, and not by a read before it. The conflict is detected by `add()` or `save()` itself, never by `commit()`, and doesn't make the transaction unusable: after it, the same transaction can try another slug.
- No use case receives a `ShortURLRepository`: it only exists as the `shorturls` of a [`Transaction`](#unit-of-work), so no use case can write outside a transaction.
- A `ShortURLReader` reads outside any transaction. Only the use cases that don't write receive one (see [Concurrency](#concurrency)).

### Unit of work

`unit_of_work.py`

`UnitOfWork.begin()` returns an async context manager that begins a `Transaction`:

```python
async with uow.begin() as transaction:
    shorturl = await transaction.shorturls.get_by_slug(slug)
    ...
    await transaction.shorturls.save(shorturl)
    await transaction.commit()
```

- `transaction.shorturls` is a `ShortURLRepository` whose reads and writes are part of the transaction.
- `commit()` makes the writes of the transaction permanent. Committing is explicit: leaving the block without calling `commit()`, by a `return` or by an exception, rolls the transaction back.

#### Concurrency

A short URL read through `transaction.shorturls` can't be changed by another transaction until this one ends, by commit or rollback. Another transaction that reads the same short URL waits for this one to end, and then reads what it wrote. How the storage keeps this contract is up to the layer that implements it.

That is why every write that depends on a read reads through the transaction, and why the use cases that write don't receive a `ShortURLReader`. `save()` stores the whole short URL, so saving one that was read outside the transaction would write back the old values of whatever another transaction changed in between, with no error: a resolution would be lost, or a short URL would be active again after being disabled. See issue 0007 and issue 0008.

### Current user

`current_user.py`

`CurrentUser.get_id()` returns the `UserID` of the user making the request, or `None` when there is no authenticated user. Asking who makes the request and getting "nobody" isn't a failure of the abstraction, so `None` isn't an error by itself: each use case decides. Those that require a user return `NotAuthenticatedError` when they get `None`. A use case that doesn't need a user doesn't receive a `CurrentUser`.

The abstraction is the user making the request, not the owner: being the owner is a role that this user has, or not, in relation to a short URL (see [Owner](domain.md#owner)). `get_id()` returns a `UserID`, the type of `ShortURL.owner_id`, so the use cases compare them without converting anything.

### Clock

`clock.py`

`Clock.now()` returns the current moment, as a timezone-aware datetime in UTC. The use cases read the clock only through it, and give its value to the domain as `now` (see [Time](domain.md#time)).

## Errors

The errors the callers of the use cases have to handle aren't exceptions: the use cases return them in a [`Result`](shared.md#result), like the domain does.

### Errors of the abstractions

| Kind                                                | Examples                                                    | How it reaches the use case                                                                                       |
| --------------------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Expected: part of the contract of the abstraction   | A slug that is taken, no authenticated user, no short URL   | A value: `Err(SlugTakenError(slug))` from `add()` and `save()`, and `None` from the reads and from `get_id()`     |
| Unexpected: a failure of the implementation, or a bug | The database is down, a timeout, an error of the driver   | An exception, which the use cases don't catch                                                                     |

### Errors of the use cases

`errors.py`

Frozen dataclasses, like the [errors of the domain](domain.md#errors), so they can be matched, as in `Err(ShortURLNotFoundError())`. The ones with no fields are equal to every other instance of their class.

| Error                   | Fields                                                                | Means                                                                                                        |
| ----------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `NotAuthenticatedError` | None                                                                  | The use case requires a user, and there is no authenticated user.                                           |
| `ShortURLNotFoundError` | None                                                                  | The short URL doesn't exist, or belongs to another user.                                                    |
| `InvalidInputError`     | `fields`: a tuple of `FieldError`                                     | Values of the input break the rules of their value objects, such as a slug that is too short.               |
| `FieldError`            | `field`: the name of the input value; `error`: its `ValidationError`  | One input value that breaks the rules of its value object, inside an `InvalidInputError`.                   |
| `NothingToUpdateError`  | None                                                                  | An update was asked for with no value to change.                                                            |

## Results

The use cases don't return entities: they return frozen dataclasses that only hold data, of primitive types.

### ShortURLDetails

`shorturl_details.py`

Every field of a [`ShortURL`](domain.md#shorturl), as primitives. `ShortURLDetails.from_entity(shorturl)` builds it:

| Field              | Type               | Value                                       |
| ------------------ | ------------------ | ------------------------------------------- |
| `id`               | `UUID`             | `shorturl.id.value`                         |
| `slug`             | `str`              | `shorturl.slug`, as a plain `str`           |
| `target_url`       | `str`              | `shorturl.target_url`, as a plain `str`     |
| `owner_id`         | `UUID`             | `shorturl.owner_id.value`                   |
| `status`           | `str`              | `shorturl.status.value`, such as `"active"` |
| `resolution_count` | `int`              | `shorturl.resolution_count`                 |
| `created_at`       | `datetime`         | `shorturl.created_at`                       |
| `last_resolved_at` | `datetime \| None` | `shorturl.last_resolved_at`                 |

## Open questions

Decisions to make during this phase. There are none at the moment.
