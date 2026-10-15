# Bootstrap

`bootstrap` assembles the application: it reads the settings, builds the implementations of [`infra`](infra.md), builds the [use cases](use_cases.md) with them, and gives them to the [API](api.md). It lives in `shortener/bootstrap/`, and is the only layer that imports from every other one.

This document describes `bootstrap` as it is in the code. Verified bugs that aren't fixed yet are [issues](issues/README.md) labeled `bootstrap`, linked from where this document describes the code they affect. Decisions still to be made are in [Open questions](#open-questions).

## Overview

```
shortener/bootstrap/
├── settings.py    Settings, DatabaseSettings, AccessTokenSettings and SettingsError
├── use_cases.py   UseCases
└── app.py         create_app() and access_token_verifier()
```

## Settings

`settings.py`

`Settings.from_environment(environment=os.environ)` reads the settings from the environment variables:

| Variable         | Required       | Value                                                                                                                                                                                   |
| ---------------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DATABASE_URL`   | Yes            | The URL of the Postgres database, with the driver of asyncpg, such as `postgresql+asyncpg://user:password@localhost:5432/shortener`. The [migrations](infra.md#migrations) read it too. |
| `JWT_ALGORITHMS` | Yes            | The algorithms an access token may be signed with, separated by commas, such as `RS256` or `HS256`                                                                                      |
| `JWT_ISSUER`     | Yes            | The issuer of the tokens, which their `iss` claim has to be                                                                                                                             |
| `JWT_AUDIENCE`   | Yes            | The audience of the tokens, which their `aud` claim has to be or have                                                                                                                   |
| `JWT_KEY`        | One of the two | The key that verifies the tokens: the secret of the HMAC algorithms, or the public key of the others, in PEM                                                                            |
| `JWT_JWKS_URL`   | One of the two | The URL where the issuer publishes the keys that verify the tokens, as a JWKS                                                                                                           |

And these optional ones, of numbers, which have a default:

| Variable                     | Default | Value                                                                                                                                                                                                    |
| ---------------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DATABASE_POOL_SIZE`         | 5       | The connections the pool of the database keeps open: 1 or more                                                                                                                                           |
| `DATABASE_MAX_OVERFLOW`      | 10      | The connections the pool opens beyond `DATABASE_POOL_SIZE` when those are all in use, and closes when they are returned: 0 or more                                                                       |
| `DATABASE_POOL_TIMEOUT`      | 30      | The most a request waits for a connection of the pool when they are all in use, in seconds: more than 0                                                                                                  |
| `DATABASE_CONNECT_TIMEOUT`   | 10      | The most the service waits to connect to the database, in seconds: more than 0                                                                                                                           |
| `DATABASE_LOCK_TIMEOUT`      | 5       | The most a statement waits for a lock, such as the one of a short URL that another transaction read, in seconds: more than 0, up to 2147483.647                                                          |
| `DATABASE_STATEMENT_TIMEOUT` | 30      | The most a statement runs, in seconds: more than 0, up to 2147483.647                                                                                                                                    |
| `JWT_LEEWAY`                 | 60      | The difference allowed between the clock of the issuer of the tokens and the one of the service, when checking the times of a token, in seconds: 0 or more (see [Access tokens](infra.md#access-tokens)) |
| `JWT_JWKS_TIMEOUT`           | 5       | The most the service waits for each step of fetching the keys from `JWT_JWKS_URL`, in seconds: more than 0. Only with `JWT_JWKS_URL` (see [Access tokens](infra.md#access-tokens))                       |

- A value is stripped of spaces, and an empty one is the same as a variable that isn't set. In `JWT_ALGORITHMS`, an empty item between commas is left out.
- A number of seconds may have decimals, such as `0.5`, and the other numbers are whole.
- It raises `SettingsError` when the variables don't make valid settings, with a message that names every problem: a required variable that is missing, a `DATABASE_URL` that isn't a URL of `postgresql+asyncpg`, both or neither of `JWT_KEY` and `JWT_JWKS_URL`, `JWT_JWKS_TIMEOUT` with `JWT_KEY`, and an optional variable that isn't a number, or is out of the range of its table.
- Otherwise, it returns a `Settings`, with the settings of the database in a `DatabaseSettings`, whose `url` is `DATABASE_URL`, `pool_size` and `max_overflow`, as `int`s, and `pool_timeout`, `connect_timeout`, `lock_timeout` and `statement_timeout`, as `timedelta`s, and the settings of the access tokens in an `AccessTokenSettings`: `algorithms`, as a tuple, `issuer`, `audience`, `key` and `jwks_url`, of which exactly one isn't `None`, and `leeway` and `jwks_timeout`, as `timedelta`s. An optional variable that isn't set gets its default, a `DEFAULT_` constant of `settings.py`, which is also the default of its field, so settings built in code can leave it out.
- `DATABASE_POOL_SIZE`, `DATABASE_MAX_OVERFLOW` and `DATABASE_POOL_TIMEOUT` have the defaults of SQLAlchemy, and `DATABASE_CONNECT_TIMEOUT` is 10 seconds, instead of the 60 of asyncpg. `DATABASE_LOCK_TIMEOUT` and `DATABASE_STATEMENT_TIMEOUT` have a default because Postgres has none: without them, a statement waits for a lock, and runs, as long as it takes. 2147483.647 seconds is the most Postgres takes for them, which it keeps as a number of milliseconds in an `int`.
- `JWT_LEEWAY` is a setting because the right value depends on the clock of the issuer of each environment.
- `JWT_JWKS_TIMEOUT` is 5 seconds by default, instead of the 30 of PyJWT, since each fetch of the keys holds a thread of the default pool of asyncio while it waits. Setting it with `JWT_KEY` is an error, since it is more likely a mistake of whoever set the variables.
- Whether the algorithms and the key can verify tokens is checked when the application is built, by [`JWTAccessTokenVerifier`](infra.md#access-tokens).
- It doesn't read a `.env` file. The variables come from the environment of the process, where uvicorn can load a file with `--env-file`.

## Use cases

`use_cases.py`

`UseCases(uow, shorturls, clock)` implements the [`UseCaseFactory`](api.md#use-cases) of the API. `build(use_case, current_user)` builds a use case with these, and raises `LookupError` for a class that isn't one of them:

| Use case                                                                   | Built with                                          |
| -------------------------------------------------------------------------- | --------------------------------------------------- |
| `ResolveSlug`                                                              | `uow` and `clock`                                   |
| `CreateShortURL`                                                           | `uow`, `current_user` and `clock`                   |
| `GetShortURL` and `ListShortURLs`                                          | `shorturls`, a `ShortURLReader`, and `current_user` |
| `UpdateShortURL`, `EnableShortURL`, `DisableShortURL` and `DeleteShortURL` | `uow` and `current_user`                            |

The API builds the use case of each request, with the user of the request. Building one doesn't connect to anything.

## The application

`app.py`

`create_app(settings=None)` returns the application:

1. It reads the settings from the environment variables when `settings` is `None`.
2. It creates the `AsyncEngine` of SQLAlchemy with `database_engine()`.
3. It builds `UseCases` with `SQLAlchemyUnitOfWork` and `SQLAlchemyShortURLReader`, on that engine, and `UTCClock`.
4. It builds the verifier of access tokens with `access_token_verifier()`.
5. It returns the application of [`create_app()`](api.md#the-application) of the API, with a lifespan that disposes the engine when the application stops.

It raises `SettingsError` for the environment variables, `ValueError` when the settings of the access tokens can't verify tokens, and `LookupError` from the API.

`database_engine(settings)` returns the `AsyncEngine` of SQLAlchemy for the `url` of the settings, with `pool_pre_ping`: the engine only connects when it is first used, and checks a connection of the pool before using it, so it replaces the ones the server closed, such as after a restart. With the other settings:

- The pool keeps up to `pool_size` connections, and opens up to `max_overflow` more when those are all in use. A request that finds them all in use waits up to `pool_timeout` for one, and then gets the `sqlalchemy.exc.TimeoutError` of SQLAlchemy.
- asyncpg waits up to `connect_timeout` to connect, and then raises `TimeoutError`.
- Each connection has the `lock_timeout` and the `statement_timeout` of the settings, which asyncpg sets when it connects. Postgres takes them in whole milliseconds, and 0 turns them off, so a fraction of a millisecond rounds up. When they run out, Postgres cancels the statement, with the SQLSTATE `55P03` or `57014`.

The implementations of the database raise `UnavailableError` from these timeouts, which are transient (see [Failures of the database](infra.md#failures-of-the-database)).

`access_token_verifier(settings)` returns a `JWTAccessTokenVerifier` with the algorithms, the issuer, the audience and the leeway of the settings: `with_jwks()`, with the `jwks_timeout`, when `jwks_url` isn't `None`, and `with_key()` otherwise. It raises `SettingsError` when both are `None`, which only settings built in code, and not by `from_environment()`, can be.

## Running

The application runs with uvicorn, which calls `create_app()` as a factory:

```bash
poetry run alembic upgrade head
poetry run uvicorn shortener.bootstrap.app:create_app --factory --host 0.0.0.0 --port 8000
```

`poetry run task run` runs it with `--reload`, for development. Both need the [environment variables](#settings).

## Open questions

Decisions to make during this phase. There are none at the moment.
