# Infrastructure

The infrastructure implements the abstractions the other layers define: those of the [use cases](use_cases.md#abstractions), such as storing short URLs, and those of the [API](api.md), such as verifying access tokens and limiting the requests. It lives in `shortener/infra/`, and imports only from the use cases, the [domain](domain.md) and [`shortener/shared/`](shared.md). It doesn't read settings, and its implementations receive what they use, such as the engine of the database: [`bootstrap`](bootstrap.md) builds them, and gives them to the layers that use them.

## Overview

```
shortener/infra/
├── clock.py                       UTCClock
├── in_memory_rate_limiter.py      InMemoryRateLimiter
├── jwt_access_token_verifier.py   JWTAccessTokenVerifier
└── db/
    ├── tables.py                  metadata, the shorturls table and SLUG_UNIQUE_CONSTRAINT
    ├── unit_of_work.py            SQLAlchemyUnitOfWork and SQLAlchemyTransaction
    ├── shorturl_repository.py     SQLAlchemyShortURLRepository and SQLAlchemyShortURLReader
    ├── health_check.py            SQLAlchemyHealthCheck
    ├── migrations.py              apply_migrations(), check_migrations(), UnexpectedMigrationsError
    │                              and MIGRATIONS_LOCK_KEY
    └── transient_errors.py        unavailable_when_transient() and is_transient()

alembic/                           the migrations of the database
```

| Abstraction                                                | Implementation                 |
| ---------------------------------------------------------- | ------------------------------ |
| [`UnitOfWork`](use_cases.md#unit-of-work)                  | `SQLAlchemyUnitOfWork`         |
| [`Transaction`](use_cases.md#unit-of-work)                 | `SQLAlchemyTransaction`        |
| [`ShortURLRepository`](use_cases.md#reading-and-writing)   | `SQLAlchemyShortURLRepository` |
| [`ShortURLReader`](use_cases.md#reading-and-writing)       | `SQLAlchemyShortURLReader`     |
| [`Clock`](use_cases.md#clock)                              | `UTCClock`                     |
| [`AccessTokenVerifier`](api.md#authentication), of the API | `JWTAccessTokenVerifier`       |
| [`RateLimiter`](api.md#rate-limit), of the API             | `InMemoryRateLimiter`          |
| [`HealthCheck`](api.md#health-check), of the API           | `SQLAlchemyHealthCheck`        |

## Database

The short URLs are stored in Postgres, through the core of SQLAlchemy (tables and statements, without the ORM) and the asyncpg driver. The implementations receive an `AsyncEngine`, which [`bootstrap`](bootstrap.md) creates.

### The shorturls table

`tables.py`

| Column             | Type                    | Value                                       |
| ------------------ | ----------------------- | ------------------------------------------- |
| `id`               | `uuid`, primary key     | `shorturl.id.value`                         |
| `slug`             | `text`, unique          | `shorturl.slug`, as a plain `str`           |
| `target_url`       | `text`                  | `shorturl.target_url`, as a plain `str`     |
| `owner_id`         | `uuid`                  | `shorturl.owner_id.value`                   |
| `status`           | `text`                  | `shorturl.status.value`, such as `"active"` |
| `resolution_count` | `bigint`                | `shorturl.resolution_count`                 |
| `created_at`       | `timestamptz`           | `shorturl.created_at`                       |
| `last_resolved_at` | `timestamptz`, nullable | `shorturl.last_resolved_at`                 |

- The unique constraint of `slug` is named `SLUG_UNIQUE_CONSTRAINT` (`uq_shorturls_slug`), which the repository uses to tell a [taken slug](#short-urls) apart from other conflicts. Postgres compares `text` case-sensitively, so `abc` and `ABC` are different slugs, as they are in the domain.
- The index `ix_shorturls_owner_id_created_at_id`, on `owner_id`, `created_at` and `id`, serves `list_by_owner()`, which filters by owner in that order, and `remove_by_owner()`, which filters by owner.
- No column limits the length of the slug or of the target URL, and no constraint checks `status` or `resolution_count`. The lengths are rules of `create()`, which can change, and a stored value has to keep loading (see [Value objects](domain.md#value-objects)).
- `owner_id` has no foreign key: the users live outside the service (see [Owner](domain.md#owner)).
- `timestamptz` stores the moment, and asyncpg returns it in UTC. A datetime stored in another timezone comes back equal to it, since aware datetimes are compared by the moment (see [Time](domain.md#time)).

### Migrations

`alembic/`

The schema is created and changed by the migrations of Alembic, and `alembic upgrade head` applies them. `alembic/env.py` runs them with asyncpg, on the URL of the `database_url` attribute of the configuration of Alembic, when whoever runs them from code sets it, as `apply_migrations()` does, or on the `DATABASE_URL` environment variable otherwise, the same one as the application (see [Configuration](../service/configuration.md#the-api)). An attribute takes the URL as it is, while an option of the configuration would read a `%`, such as the one of a password encoded in the URL, as an interpolation.

`alembic/env.py` runs the migrations in a single transaction, which first takes the advisory lock of `MIGRATIONS_LOCK_KEY`, with `pg_advisory_xact_lock()`, until it ends. Another process that migrates the same database waits for the lock, and then reads what the first one committed, so it applies only the migrations still missing, if any. Its engine has none of the timeouts of the [settings](bootstrap.md#the-database), so it waits for the lock, and runs the migrations, as long as they take.

`migrations.py`

`apply_migrations(database_url)` applies the migrations up to the last one, as `alembic upgrade head` does, on the database of `database_url`, and raises the errors of Alembic and of the database as they are. It runs them in a thread, since `alembic/env.py` runs them in an event loop of its own, which can't run in the one of the caller. It finds `alembic/` beside the package `shortener`, where the image has it too. The `context` of Alembic is one for the whole process, so two calls at once in the same process would break each other: a process calls it once, when it starts (see [Migrating on start](../service/running.md#migrating-on-start)).

`check_migrations(engine)` reads the last migrations the database has, from the table of Alembic, with a connection of the engine, and raises `UnexpectedMigrationsError` when they aren't the last ones of `alembic/`: when the database has none, such as when it was never migrated, when it has an earlier one, or when it has one the code doesn't know. Its `applied` and `expected` are the identifiers of the migrations of the database and of the code, as tuples, and its message names them. It raises the errors of the database as they are, such as the `OSError` of a server that can't be reached.

A migration is generated by `alembic revision --autogenerate`, against a database migrated up to the previous one, and then reviewed. `tests/test_infra/test_db/test_migrations.py` checks that a database migrated to the last one has the tables `tables.py` describes, so a change to `tables.py` without its migration fails the tests.

### Unit of work

`unit_of_work.py`

`SQLAlchemyUnitOfWork(engine)` implements [`UnitOfWork`](use_cases.md#unit-of-work). `begin()` takes a connection from the pool of the engine, and returns a `SQLAlchemyTransaction` on it, whose `shorturls` is a [`SQLAlchemyShortURLRepository`](#short-urls) on the same connection.

- Postgres begins the transaction at the first statement, with its default isolation, `READ COMMITTED`.
- `commit()` commits the transaction.
- Leaving the block, by a `return` or an exception, closes the connection, which rolls back what wasn't committed, and returns it to the pool.

### Short URLs

`shorturl_repository.py`

`SQLAlchemyShortURLRepository(connection)` implements [`ShortURLRepository`](use_cases.md#reading-and-writing), and is the `shorturls` of a `SQLAlchemyTransaction`. `SQLAlchemyShortURLReader(engine)` implements `ShortURLReader`, and reads outside any transaction. Both read with the same statements:

| Method                                  | Rows                                                                                                                                                                                                                |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_by_id(id)`                         | The one whose `id` is `id.value`                                                                                                                                                                                    |
| `get_by_slug(slug)`                     | The one whose `slug` is `slug`                                                                                                                                                                                      |
| `list_by_owner(owner_id, limit, after)` | Those whose `owner_id` is `owner_id.value`, ordered by `created_at` and then `id`, both descending, up to `limit`. With `after`, only those whose `(created_at, id)` is smaller than `(after.created_at, after.id)` |

A row becomes a `ShortURL` with `ShortURL.restore()`, and its slug and target URL with [`parse()`](domain.md#value-objects), so a value stored under older rules of `create()` still loads.

The two differ in how they read:

- **The repository of a transaction** reads with `SELECT ... FOR UPDATE`, which keeps the [contract of concurrency](use_cases.md#concurrency): the rows it reads stay locked until the transaction ends, and another transaction that reads them through its own repository waits until then. When the first one commits, Postgres reads the rows again for the one that waited, which gets what the first one wrote: the new values, `None` when it removed the short URL, and, reading by slug, `None` when it changed the slug. When the first one rolls back, the one that waited reads the rows as they were. `list_by_owner()` locks every row it returns. A read waits for the lock up to the `lock_timeout` of the connection, which [`bootstrap`](bootstrap.md#the-database) sets, and then raises `UnavailableError`, since Postgres answers `55P03`, which is [transient](#failures-of-the-database).
- **The reader** runs each read in a connection of its own, without `FOR UPDATE`: it doesn't wait for locks, and reads only what was committed.

The repository writes with these statements:

| Method                             | Statement                                                                                                                 |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `add(shorturl)`                    | `INSERT`, with every field                                                                                                |
| `save(shorturl)`                   | `UPDATE`, with every field but `id`, of the row whose `id` is the one of the short URL                                    |
| `remove(shorturl)`                 | `DELETE` of the row whose `id` is the one of the short URL                                                                |
| `remove_by_owner(owner_id, limit)` | `DELETE` of up to `limit` rows whose `owner_id` is `owner_id.value`, which a subquery with `LIMIT` and `FOR UPDATE` picks |

- `add()` and `save()` run their statement in a savepoint. When it breaks `SLUG_UNIQUE_CONSTRAINT`, the savepoint is rolled back, and they return `Err(SlugTakenError(shorturl.slug))`: only that statement is undone, and the transaction goes on. Any other `IntegrityError`, such as an `id` that is already stored, is raised.
- Postgres checks the slug when the statement runs. When another transaction wrote the same slug and hasn't ended, the statement waits for it, up to the `lock_timeout`, and only conflicts if that transaction commits.
- `save()` and `remove()` of a short URL that isn't stored change nothing, and raise nothing, nor does `remove_by_owner()` of an owner without short URLs, which returns `0`.
- `remove_by_owner()` returns the number of rows the `DELETE` deleted. Which rows of the owner it picks isn't specified.
- The subquery of `remove_by_owner()` locks the rows it picks as a read does, so it waits for the ones another transaction read through its repository, or wrote, up to the `lock_timeout`, and then raises `UnavailableError`. When that transaction removed a row, the subquery skips it once the transaction ends, and picks another row of the owner in its place, if there is one, so `remove_by_owner()` returns `0` only when the owner has no short URL left. Without `FOR UPDATE`, the `DELETE` would skip that row with no other in its place, and could return `0` while the owner still has short URLs.

### Health check

`health_check.py`

`SQLAlchemyHealthCheck(engine)` implements the [`HealthCheck`](api.md#health-check) of the API. `check()` takes a connection from the pool of the engine, runs `SELECT 1` on it, and returns it to the pool.

- It raises `UnavailableError` when the database can't answer for a [transient](#failures-of-the-database) failure, such as a server that can't be reached, and the other errors as they are, such as the `InvalidCatalogNameError` of asyncpg, when connecting to a database that doesn't exist.
- It waits as the reads of the short URLs do: up to the `pool_timeout` for a connection, when they are all in use, and up to the `connect_timeout` to connect (see [The database](bootstrap.md#the-database)).

### Failures of the database

`transient_errors.py`

The implementations of the database raise [`UnavailableError`](use_cases.md#unavailableerror) from the failures that trying again may fix, with `raise UnavailableError() from error`. They do it with the context manager `unavailable_when_transient()`, around getting a connection, every statement and `commit()`. It raises `UnavailableError` when `is_transient(error)` is true, and lets every other error through as it is.

| Failure                                                                        | How it is raised                                                                                   | Transient                                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The server can't be reached, such as a refused connection or a timeout         | `OSError`, raised by asyncpg without SQLAlchemy wrapping it                                        | Yes                                                                                                                                                                                                                                                                                                               |
| No connection of the pool became free within its timeout                       | `sqlalchemy.exc.TimeoutError`                                                                      | Yes                                                                                                                                                                                                                                                                                                               |
| The connection was lost                                                        | A `DBAPIError` whose `connection_invalidated` is true                                              | Yes                                                                                                                                                                                                                                                                                                               |
| asyncpg is in a broken state, such as after a connection lost in a transaction | `InternalClientError` of asyncpg, without SQLAlchemy wrapping it                                   | Yes                                                                                                                                                                                                                                                                                                               |
| Postgres answered an error                                                     | A `DBAPIError` whose `orig` has the SQLSTATE, or, when connecting, an error of asyncpg that has it | When the SQLSTATE is of the classes `08` (connection exception) or `53` (insufficient resources), or is `40001` (serialization failure), `40P01` (deadlock), `55P03` (lock not available), `57014` (query canceled, such as by `statement_timeout`), `57P01`, `57P02` (shutdowns) or `57P03` (cannot connect now) |
| Anything else                                                                  |                                                                                                    | No                                                                                                                                                                                                                                                                                                                |

Errors that trying again won't fix are raised as they are, such as `42P01` (a table that doesn't exist), `28P01` (a wrong password) or `3D000` (a database that doesn't exist).

asyncpg raises `InternalClientError` for every broken state of its protocol, such as when the server ended the session of a transaction, and asyncpg hasn't noticed yet that the connection was closed. It can't be told apart from the other broken states, by its type or by whether the connection is closed, and its message changes with the versions of asyncpg, so every `InternalClientError` is transient. No code of the project raises it, and the connection can't be used after it either way. The cost is that a bug of asyncpg is answered as unavailable too, still with its cause. SQLAlchemy doesn't invalidate the connection, which goes back to the pool, and the `pool_pre_ping` of the engine replaces it the next time it is taken (see [The database](bootstrap.md#the-database)).

A connection lost during `commit()` is transient too, even when Postgres committed the transaction before the connection was lost, so trying again can run a use case twice ([issue 0018](../issues/0018-a-commit-whose-result-is-unknown-is-answered-as-unavailable.md)).

## Clock

`clock.py`

`UTCClock` implements [`Clock`](use_cases.md#clock). `now()` returns the current moment of the system, as a datetime in UTC. The domain accepts any timezone (see [Time](domain.md#time)), and UTC is the one this implementation chooses.

## Access tokens

`jwt_access_token_verifier.py`

`JWTAccessTokenVerifier` implements the [`AccessTokenVerifier`](api.md#authentication) of the API: it verifies access tokens that are JWTs, with PyJWT, and returns the `UserID` of the user each one was issued to. The tokens are issued outside the service (see [Scope](../../README.md#scope)). It is built in one of two ways, by where the keys that verify the signatures come from:

| Way                                                             | Keys                                                                                                                    |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `with_key(key, algorithms, issuer, audience, leeway)`           | A single key: the secret of the HMAC algorithms (`HS256`, `HS384` and `HS512`), or the public key of the others, in PEM |
| `with_jwks(url, algorithms, issuer, audience, leeway, timeout)` | The keys the issuer publishes at a JWKS URL, each with its key ID (`kid`)                                               |

`algorithms` are the ones a token may be signed with: any algorithm of PyJWT but `none`, and at least one. Both ways raise `ValueError` when an algorithm isn't one of them. `with_key()` also raises it when the key doesn't suit one of the algorithms: when PyJWT can't load it for the algorithm, such as a public key as the secret of an HMAC algorithm, or when it is shorter than the algorithm needs, such as a secret shorter than the hash of an HMAC algorithm. `with_jwks()` also raises it when the URL isn't `http` or `https`. `leeway`, a `timedelta`, is the difference allowed between the clock of the issuer and the one of the service, when checking the times of a token. `timeout`, a `timedelta` too, is the most `with_jwks()` waits for each step of fetching the keys, such as connecting to the URL or receiving a part of its answer, so an answer that keeps arriving slowly can take longer.

`verify(token)` returns the `UserID` of the UUID in the `sub` claim, when the token:

- is a JWT signed with one of `algorithms`: by the key, or by the published key whose `kid` is the one in the header of the token, and whose algorithm is the one of the token;
- has `exp`, and `sub`, a string with a UUID;
- has `iss`, equal to `issuer`, when `issuer` isn't `None`, and any `iss`, or none, when it is;
- has `aud`, equal to `audience` or a list that has it, when `audience` isn't `None`, and no `aud` when it is, as PyJWT checks by default (see [Access tokens](../service/api.md#access-tokens));
- has an `exp` later than the current time minus `leeway`, and `nbf` and `iat`, when it has them, no later than the current time plus `leeway`.

Otherwise, it returns `None`, whatever is wrong with the token. Without the leeway, a clock of the issuer ahead of the one of the service would make a new token not valid yet, for as long as the difference. With it, a token is also accepted for up to `leeway` after its `exp`.

With JWKS, PyJWT fetches the published keys when it needs them, in a thread, since it fetches with urllib, which blocks. It keeps them for 5 minutes, and, for a `kid` it doesn't have, fetches them again at most once every 30 seconds, so a token with an unknown `kid` doesn't make every request fetch them. `verify()` raises `UnavailableError`, from the error of PyJWT or of `json`, when the keys can't be fetched, because the URL can't be reached, takes longer than `timeout` or answers an HTTP error, and when the answer isn't a set of signing keys: it isn't JSON, isn't a JSON object, has no key PyJWT can use, or has no signing key with a `kid`. Neither is a problem of the token, and the service can't tell a wrong setting from a failure of the issuer. A token whose `kid` isn't in a set of signing keys is still not valid, and `verify()` returns `None` for it. PyJWT raises `PyJWKClientError` for both, so the verifier uses a subclass of `PyJWKClient` whose `get_signing_keys()`, which every fetch of the keys goes through, raises `UnavailableError` from its errors.

PyJWT keeps a set of keys without a signing key for 5 minutes, as any other set, so `verify()` raises `UnavailableError` until then, without fetching the keys again. It doesn't keep the other answers, and fetches the keys again at the next `verify()`.

## Rate limit

`in_memory_rate_limiter.py`

`InMemoryRateLimiter(requests, window, clock)` implements the [`RateLimiter`](api.md#rate-limit) of the API: it allows each key up to `requests` requests in each window of time of `window`, a `timedelta`, and counts them in the memory of the process, with the time of `clock`, a [`Clock`](use_cases.md#clock).

`hit(key)` counts a request of the key, and returns `None` while the count of the key in the current window is up to `requests`, and, for each request after that, the time until the window ends.

- There is one window for every key. It starts with the first request after the previous one ended, and lasts `window`. When it ends, the counts of every key are forgotten, and start again from 0.
- The counts are in a `dict` of the instance, so they are of the process, and a restart forgets them.
- `hit()` doesn't await anything, so in the event loop no other request counts while it runs.
- What that means for the clients, such as up to twice `requests` in a short time, at the end of one window and the start of the next, and a count in each process, is in [Rate limit](../service/api.md#rate-limit).
- With the [`UTCClock`](#clock) that [`bootstrap`](bootstrap.md#the-application) gives it, a change of the time of the system changes when the current window ends.
