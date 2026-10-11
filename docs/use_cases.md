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
├── unavailable_error.py     UnavailableError
├── errors.py                NotAuthenticatedError, ShortURLNotFoundError, InvalidInputError,
│                            FieldError, NothingToUpdateError and collect_field_errors()
├── shorturl_details.py      ShortURLDetails
├── shorturl_page.py         ShortURLPage
├── shorturl_cursor.py       ShortURLCursor
├── resolved_slug.py         ResolvedSlug
├── resolve_slug.py          ResolveSlug
├── create_shorturl.py       CreateShortURL
├── get_shorturl.py          GetShortURL
├── list_shorturls.py        ListShortURLs
├── update_shorturl.py       UpdateShortURL
├── enable_shorturl.py       EnableShortURL
├── disable_shorturl.py      DisableShortURL
└── delete_shorturl.py       DeleteShortURL
```

## Abstractions

The abstractions are `Protocol`s, so the other layers implement them without inheriting anything. The use cases receive the implementations in their constructors.

### Reading and writing

`shorturl_repository.py`

`ShortURLReader` reads short URLs:

| Method                                  | Returns                                                                                        |
| --------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `get_by_id(id)`                         | The short URL whose `id` is the given `ShortURLID`, or `None` when there is none.             |
| `get_by_slug(slug)`                     | The short URL whose `slug` is the given `Slug`, or `None` when there is none.                 |
| `list_by_owner(owner_id, limit, after)` | A list of at most `limit` short URLs whose `owner_id` is the given `UserID`, empty when there are none. See [Listing order](#listing-order). |

#### Listing order

`list_by_owner()` returns the short URLs newest first: by `created_at` descending, and by `id` descending among those with the same `created_at`. Every short URL has its own `id`, so the order is total.

`after` is a [`ShortURLCursor`](#shorturlcursor) or `None`. With a cursor, it returns only the short URLs that come after it in this order: those with an earlier `created_at`, or with the same `created_at` and a smaller `id`. It compares the values of the cursor, and doesn't read the short URL they came from, so a cursor keeps working after that short URL is deleted or changed. With `None`, it starts from the newest.

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

That is why every write that depends on a read reads through the transaction, and why the use cases that write don't receive a `ShortURLReader`. `save()` stores the whole short URL, so saving one that was read outside the transaction would write back the old values of whatever another transaction changed in between, with no error: a resolution would be lost, or a short URL would be active again after being disabled. The use cases do their part, and [`infra`](infra.md#short-urls) keeps the contract by locking what a transaction reads.

### Current user

`current_user.py`

`CurrentUser.get_id()` returns the `UserID` of the user making the request, or `None` when there is no authenticated user. Asking who makes the request and getting "nobody" isn't a failure of the abstraction, so `None` isn't an error by itself: each use case decides. Those that require a user return `NotAuthenticatedError` when they get `None`. A use case that doesn't need a user doesn't receive a `CurrentUser`.

The abstraction is the user making the request, not the owner: being the owner is a role that this user has, or not, in relation to a short URL (see [Owner](domain.md#owner)). `get_id()` returns a `UserID`, the type of `ShortURL.owner_id`, so the use cases compare them without converting anything.

### Clock

`clock.py`

`Clock.now()` returns the current moment, as a timezone-aware datetime. The use cases don't generate datetimes: they read the clock only through it, and give its value to the domain as `now` (see [Time](domain.md#time)). The domain requires a timezone-aware `now`, so the use cases rely on `Clock` to return one, and don't check it: a naive one raises `ValueError`, from the domain. Which timezone it is in, such as UTC, is guaranteed by the implementation, in `infra`.

## Errors

The errors the callers of the use cases have to handle aren't exceptions: the use cases return them in a [`Result`](shared.md#result), like the domain does.

### Errors of the abstractions

| Kind                                                        | Examples                                                                            | How it reaches the use case                                                                                   |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Expected: part of the contract of the abstraction           | A slug that is taken, no authenticated user, no short URL                           | A value: `Err(SlugTakenError(slug))` from `add()` and `save()`, and `None` from the reads and from `get_id()` |
| Unavailable: a failure that trying again may fix            | The database is down, a timeout, no free connection, a wait for a lock that ran out | [`UnavailableError`](#unavailableerror), which the use cases don't catch                                      |
| Unexpected: a bug, or a failure that trying again won't fix | A table that doesn't exist, an error in a mapper                                    | The exception the implementation raised, which the use cases don't catch                                      |

#### UnavailableError

`unavailable_error.py`

`UnavailableError` is the exception the implementations of the abstractions raise when they can't do what they were asked now, for a reason that is expected to go away, so trying the operation again may succeed. They raise it with `raise UnavailableError() from error`, so the exception of the library stays in `__cause__`.

- They raise it only for those failures. A failure that trying again won't fix, or that isn't known to go away, is raised as it is: wrapping a bug would tell the caller to try again, and nothing would flag it. The class of the exception of the library isn't always enough to tell them apart: on SQLite, `no such table` and `database is locked` are both an `OperationalError`.
- It has no subclasses and no fields, since the caller does the same whatever failed. What failed is in `__cause__`.
- It is an exception, and not an `Err`, since no use case handles it: it goes through `execute()`, and through `async with uow.begin()`, which rolls the transaction back.

With it, the caller tells these failures apart from bugs without importing the exceptions of each library, such as answering 503 to `UnavailableError` and 500 to any other exception. The implementations of the database raise it, as [Failures of the database](infra.md#failures-of-the-database) describes, and the API answers 503 to it (see [Errors](api.md#errors)).

### Errors of the use cases

`errors.py`

Frozen dataclasses, like the [errors of the domain](domain.md#errors), so they can be matched, as in `Err(ShortURLNotFoundError())`. The ones with no fields are equal to every other instance of their class.

| Error                   | Fields                                                                | Means                                                                                                        |
| ----------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `NotAuthenticatedError` | None                                                                  | The use case requires a user, and there is no authenticated user.                                           |
| `ShortURLNotFoundError` | None                                                                  | The short URL doesn't exist, or belongs to another user.                                                    |
| `InvalidInputError`     | `fields`: a tuple of `FieldError`                                     | Values of the input break their rules, such as a slug that is too short, or a limit above the maximum.      |
| `FieldError`            | `field`: the name of the input value; `error`: its `ValidationError`  | One input value that breaks its rules, inside an `InvalidInputError`.                                       |
| `NothingToUpdateError`  | None                                                                  | An update was asked for with no value to change.                                                            |

`collect_field_errors(**results)` builds the `FieldError`s of an input. It takes the `Result` of the validation of each input value, such as the `create()` of a value object, as a keyword argument named after the value, and returns a tuple with a `FieldError` for each `Err`, in the order of the arguments. When every result is `Ok`, the tuple is empty.

## Results

The use cases don't return entities: they return frozen dataclasses that only hold data, of primitive types or other results.

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

### ShortURLPage

`shorturl_page.py`

What [`ListShortURLs`](#listshorturls) returns: one page of the short URLs of a user.

| Field         | Type                          | Value                                                                |
| ------------- | ----------------------------- | -------------------------------------------------------------------- |
| `items`       | `tuple[ShortURLDetails, ...]` | The `ShortURLDetails` of the short URLs of the page, in order        |
| `next_cursor` | `ShortURLCursor \| None`     | Where the next page starts, or `None` when there is no next page     |

### ShortURLCursor

`shorturl_cursor.py`

The position of a short URL in the [listing order](#listing-order): its `created_at`, as a `datetime`, and its `id`, as a `UUID`. `ShortURLCursor.from_entity(shorturl)` builds it. [`ListShortURLs`](#listshorturls) returns it as the `next_cursor` of a page, and receives it back to read the next one.

### ResolvedSlug

`resolved_slug.py`

What [`ResolveSlug`](#resolveslug) returns: only `target_url`, as a plain `str`, since that is what the caller needs to redirect, and it already has the slug. `ResolvedSlug.from_target_url(target_url)` builds it from a `TargetURL`.

## Use cases

Each use case is a class whose constructor receives the abstractions it uses, and whose `execute()` carries out the operation. `execute()` returns a `Result`: `Ok` with one of the [results](#results), or `Err` with one of the errors of a union named after the use case, such as `ResolveSlugError`. The errors of the domain and of the abstractions are returned as they are.

The target URL and the slug are received as `str`, and the use case turns them into their value objects, since the domain has rules about them that the client can break, returned as an `InvalidInputError` (see [`CreateShortURL`](#createshorturl)). The ID of a short URL is received as a `UUID`, and the caller converts it from whatever its transport carries, such as a string in the path of a request. The domain has no rule about IDs besides being a `UUID`, so a string that isn't one is a parsing failure of the transport, like malformed JSON, and not an input error of the use case. That is why an `id` that isn't a `UUID` raises `TypeError`, as a programming error, and `ShortURLDetails` returns the IDs as `UUID` too.

A use case that writes commits only when it succeeds. When it returns `Err`, it leaves the transaction without calling `commit()`, which rolls it back.

A use case that receives the ID of a short URL only acts on the short URLs of the user making the request: one that belongs to another user gets the same `ShortURLNotFoundError` as one that doesn't exist.

### ResolveSlug

`resolve_slug.py`

`ResolveSlug(uow, clock)` resolves a slug to its target URL, and counts the resolution. Anyone can resolve a slug, so it doesn't receive a `CurrentUser`.

`execute(slug)` returns `Result[ResolvedSlug, ResolveSlugError]`, where `ResolveSlugError` is `ShortURLNotFoundError | ShortURLDeactivatedError`:

1. It turns `slug` into a `Slug` with [`Slug.parse()`](domain.md#value-objects), so a slug created under older rules still resolves. A `slug` that isn't a `str` raises `TypeError`, and an empty one raises `ValueError`, before any transaction begins.
2. It begins a transaction and reads the short URL with `get_by_slug()`. When there is none, it returns `Err(ShortURLNotFoundError())`.
3. It calls `resolve()` with `Clock.now()`. When the short URL is deactivated, `resolve()` returns `Err(ShortURLDeactivatedError())`, and the use case returns it without saving anything.
4. Otherwise, it saves the short URL, with the resolution counted, commits, and returns `Ok` with the `ResolvedSlug` of the target URL.

The slug of the short URL doesn't change, so `save()` can't return `SlugTakenError`. If it does, the use case raises `ValueError` with it, through `unwrap()`, without committing.

### CreateShortURL

`create_shorturl.py`

`CreateShortURL(uow, current_user, clock)` creates a short URL owned by the user making the request.

`execute(target_url, slug=None)` returns `Result[ShortURLDetails, CreateShortURLError]`, where `CreateShortURLError` is `NotAuthenticatedError | InvalidInputError | SlugTakenError`:

1. When `CurrentUser.get_id()` returns `None`, it returns `Err(NotAuthenticatedError())`, before checking the input.
2. It checks `target_url` with `TargetURL.create()`, and `slug` with `Slug.create()` when it isn't `None`: an empty `slug` is checked like any other. When values break their rules, it returns `Err(InvalidInputError(...))`, with a `FieldError` for each of them, named `target_url` or `slug`, in that order.
3. It begins a transaction, creates the short URL with `ShortURL.create()`, owned by the user and with `Clock.now()` as `now`, and adds it:
   - With a `slug`, when `add()` returns `Err(SlugTakenError(slug))`, it returns it, without trying another slug.
   - Without one, the slug comes from `Slug.generate()`. When `add()` returns `SlugTakenError`, it creates another short URL, with another generated slug, and adds it, up to `MAX_GENERATED_SLUG_ATTEMPTS` (10) attempts. When every generated slug is taken, it raises `RuntimeError`, without committing.
4. It commits, and returns `Ok` with the `ShortURLDetails` of the short URL.

### GetShortURL

`get_shorturl.py`

`GetShortURL(shorturls, current_user)` returns a short URL of the user making the request. It only reads, so it receives a `ShortURLReader`, and doesn't begin a transaction.

`execute(id)` returns `Result[ShortURLDetails, GetShortURLError]`, where `GetShortURLError` is `NotAuthenticatedError | ShortURLNotFoundError`:

1. When `CurrentUser.get_id()` returns `None`, it returns `Err(NotAuthenticatedError())`, without reading anything.
2. It reads the short URL with `get_by_id()`, with `id` as a `ShortURLID`. An `id` that isn't a `UUID` raises `TypeError`, from `ShortURLID`.
3. When there is no short URL, or it belongs to another user, it returns `Err(ShortURLNotFoundError())`.
4. Otherwise, it returns `Ok` with the `ShortURLDetails` of the short URL.

### ListShortURLs

`list_shorturls.py`

`ListShortURLs(shorturls, current_user)` lists the short URLs of the user making the request, one page at a time. It only reads, so it receives a `ShortURLReader`, and doesn't begin a transaction.

`execute(limit=DEFAULT_PAGE_SIZE, cursor=None)` returns `Result[ShortURLPage, ListShortURLsError]`, where `ListShortURLsError` is `NotAuthenticatedError | InvalidInputError`. `limit` is the most short URLs the page holds, `DEFAULT_PAGE_SIZE` (20) by default. `cursor` is the `next_cursor` of the previous page, or `None` for the first page.

1. When `CurrentUser.get_id()` returns `None`, it returns `Err(NotAuthenticatedError())`, before checking the input.
2. It checks `limit` with [`IntegerValidation`](shared.md#validation): an `int`, but not a `bool`, from 1 to `MAX_PAGE_SIZE` (100). When it isn't, it returns `Err(InvalidInputError(...))`, with a `FieldError` named `limit`, whose issue is `INVALID_TYPE`, `TOO_SMALL` or `TOO_LARGE`.
3. It reads the short URLs of the user after `cursor` with `list_by_owner()`, with `limit + 1` as the limit: the extra short URL only tells whether there is a next page.
4. It returns `Ok` with a [`ShortURLPage`](#shorturlpage). Its `items` are the `ShortURLDetails` of the first `limit` short URLs read, in the order `list_by_owner()` returned them. When it read more than `limit`, `next_cursor` is the `ShortURLCursor` of the last short URL of the page. Otherwise, it is `None`. A user with no short URLs gets a page with no items and no `next_cursor`.

`cursor` is given to `list_by_owner()` as it is, without being checked. Turning it into what the client sends and back, and rejecting a malformed one, is up to the API (see [Cursors](api.md#cursors)).

The listing is paginated from the start, so that a response doesn't grow with the number of short URLs of the user, and the API doesn't have to break its contract to paginate later. It is paginated by cursor, and not by offset, so that a page doesn't skip or repeat short URLs when others are created or deleted between pages.

### UpdateShortURL

`update_shorturl.py`

`UpdateShortURL(uow, current_user)` changes the target URL, the slug, or both, of a short URL of the user making the request.

`execute(id, target_url=None, slug=None)` returns `Result[ShortURLDetails, UpdateShortURLError]`, where `UpdateShortURLError` is `NotAuthenticatedError | NothingToUpdateError | InvalidInputError | ShortURLNotFoundError | SlugTakenError`. A value that is `None` isn't changed. That isn't ambiguous, since neither the target URL nor the slug can be `None`.

1. When `CurrentUser.get_id()` returns `None`, it returns `Err(NotAuthenticatedError())`, before checking the input.
2. When `target_url` and `slug` are both `None`, it returns `Err(NothingToUpdateError())`.
3. It checks the values that aren't `None` like [`CreateShortURL`](#createshorturl) does, and returns `Err(InvalidInputError(...))` when they break their rules. Then an `id` that isn't a `UUID` raises `TypeError`, from `ShortURLID`, before any transaction begins.
4. It begins a transaction, and reads the short URL through it with `get_by_id()`. When there is none, or it belongs to another user, it returns `Err(ShortURLNotFoundError())`.
5. It changes the given values, with `change_target_url()` and `change_slug()`, and saves the short URL. When `save()` returns `Err(SlugTakenError(slug))`, it returns it, without committing.
6. It commits, and returns `Ok` with the `ShortURLDetails` of the short URL.

The target URL and the slug change in a single call so that the change is atomic: each use case begins its own transaction, and changing them in two calls could save the target URL and then fail because the slug is taken.

### EnableShortURL and DisableShortURL

`enable_shorturl.py` and `disable_shorturl.py`

`EnableShortURL(uow, current_user)` makes a short URL of the user making the request active, with `enable()`, and `DisableShortURL(uow, current_user)` deactivates it, with `disable()`. They only differ in the method they call.

`execute(id)` returns `Result[ShortURLDetails, EnableShortURLError]` or `Result[ShortURLDetails, DisableShortURLError]`, both `NotAuthenticatedError | ShortURLNotFoundError`:

1. When `CurrentUser.get_id()` returns `None`, it returns `Err(NotAuthenticatedError())`. Then an `id` that isn't a `UUID` raises `TypeError`, from `ShortURLID`, before any transaction begins.
2. It begins a transaction, and reads the short URL through it with `get_by_id()`. When there is none, or it belongs to another user, it returns `Err(ShortURLNotFoundError())`.
3. It calls `enable()` or `disable()`, saves the short URL, commits, and returns `Ok` with the `ShortURLDetails` of the short URL. When the short URL is already in the status the method leads to, the method changes nothing, and the use case still saves it and commits.

The slug of the short URL doesn't change, so `save()` can't return `SlugTakenError`. If it does, the use case raises `ValueError` with it, through `unwrap()`, without committing.

The status isn't changed by `UpdateShortURL`: [`ShortURLStatus`](domain.md#status) has no `create()` that returns a `ValidationError`, so an invalid status couldn't come back as a `FieldError`. These use cases only receive the ID, and follow the methods of the domain. They are almost the same, and that repetition is accepted: two uses don't justify an abstraction.

### DeleteShortURL

`delete_shorturl.py`

`DeleteShortURL(uow, current_user)` deletes a short URL of the user making the request.

`execute(id)` returns `Result[None, DeleteShortURLError]`, where `DeleteShortURLError` is `NotAuthenticatedError | ShortURLNotFoundError`:

1. When `CurrentUser.get_id()` returns `None`, it returns `Err(NotAuthenticatedError())`. Then an `id` that isn't a `UUID` raises `TypeError`, from `ShortURLID`, before any transaction begins.
2. It begins a transaction, and reads the short URL through it with `get_by_id()`, to check its owner. When there is none, or it belongs to another user, it returns `Err(ShortURLNotFoundError())`.
3. It removes the short URL with `remove()`, commits, and returns `Ok(None)`.

## Open questions

Decisions to make during this phase. There are none at the moment.
