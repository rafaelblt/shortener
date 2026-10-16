# Bootstrap

`bootstrap` assembles the application: it reads the settings, builds the implementations of [`infra`](infra.md), builds the [use cases](use_cases.md) with them, and gives them to the [API](api.md) and to the [consumer](consumer.md), which run as two processes. It lives in `shortener/bootstrap/`, and is the only layer that imports from every other one.

How to run the two processes, and what they need around them, is in [docs/service/running.md](../service/running.md).

## Overview

```
shortener/bootstrap/
├── settings.py    Settings, ConsumerSettings, DatabaseSettings, AccessTokenSettings,
│                  RateLimitSettings and SettingsError
├── use_cases.py   UseCases
├── database.py    database_engine()
├── app.py         create_app() and access_token_verifier()
└── consumer.py    run_consumer() and main()
```

## Settings

`settings.py`

`Settings.from_environment(environment=os.environ)` reads the settings of the API from the environment variables, and `ConsumerSettings.from_environment(environment=os.environ)` the ones of the [consumer](#the-consumer), which has no access tokens or rate limit, so it doesn't read their variables. The variables, their defaults and rules, and the reasons for the defaults, are in [Configuration](../service/configuration.md).

Both read every variable before deciding, through `_Variables`, which keeps each problem it finds, so when the variables don't make valid settings they raise a single `SettingsError`, whose message names every problem. Otherwise, they return frozen dataclasses:

| Dataclass             | Fields                                                                                                                                                                 |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Settings`            | `database`, a `DatabaseSettings`, `access_tokens`, an `AccessTokenSettings`, and `rate_limit`, a `RateLimitSettings`                                                   |
| `ConsumerSettings`    | `database`, a `DatabaseSettings`, and `rabbitmq_url`, as it is                                                                                                         |
| `DatabaseSettings`    | `url`, the `DATABASE_URL`, `pool_size` and `max_overflow`, as `int`s, and `pool_timeout`, `connect_timeout`, `lock_timeout` and `statement_timeout`, as `timedelta`s   |
| `AccessTokenSettings` | `algorithms`, as a tuple, `issuer`, `audience`, `key` and `jwks_url`, of which `from_environment()` sets exactly one, and `leeway` and `jwks_timeout`, as `timedelta`s |
| `RateLimitSettings`   | `requests`, as an `int`, and `window`, as a `timedelta`                                                                                                                |

- An optional variable that isn't set gets its default, a `DEFAULT_` constant of `settings.py`, which is also the default of its field, so settings built in code, such as the ones of the tests, can leave it out. The `rate_limit` of `Settings` is a `RateLimitSettings` with the defaults, so they can leave it out too.
- `ConsumerSettings` reads the variables of the database as `Settings` does, with the same function.
- Whether the algorithms and the key can verify tokens isn't checked here, but when the application is built, by [`JWTAccessTokenVerifier`](infra.md#access-tokens).

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
2. It creates the `AsyncEngine` of SQLAlchemy with [`database_engine()`](#the-database).
3. It builds `UseCases` with `SQLAlchemyUnitOfWork` and `SQLAlchemyShortURLReader`, on that engine, and `UTCClock`.
4. It builds the verifier of access tokens with `access_token_verifier()`.
5. It builds an `InMemoryRateLimiter` with the `requests` and the `window` of the settings of the rate limit, and the same `UTCClock`.
6. It returns the application of [`create_app()`](api.md#the-application) of the API, with `SQLAlchemyHealthCheck`, on that engine, as its [health check](api.md#health-check), and a lifespan that disposes the engine when the application stops.

It raises `SettingsError` for the environment variables, `ValueError` when the settings of the access tokens can't verify tokens, and `LookupError` from the API.

`access_token_verifier(settings)` returns a `JWTAccessTokenVerifier` with the algorithms, the issuer, the audience and the leeway of the settings: `with_jwks()`, with the `jwks_timeout`, when `jwks_url` isn't `None`, and `with_key()` otherwise. It raises `SettingsError` when both are `None`, which only settings built in code, and not by `from_environment()`, can be.

## The database

`database.py`

`database_engine(settings)` returns the `AsyncEngine` of SQLAlchemy for the `url` of the settings, with `pool_pre_ping`: the engine only connects when it is first used, and checks a connection of the pool before using it, so it replaces the ones the server closed, such as after a restart. With the other settings:

- The pool keeps up to `pool_size` connections, and opens up to `max_overflow` more when those are all in use. A request that finds them all in use waits up to `pool_timeout` for one, and then gets the `sqlalchemy.exc.TimeoutError` of SQLAlchemy.
- asyncpg waits up to `connect_timeout` to connect, and then raises `TimeoutError`.
- Each connection has the `lock_timeout` and the `statement_timeout` of the settings, which asyncpg sets when it connects. Postgres takes them in whole milliseconds, and 0 turns them off, so a fraction of a millisecond rounds up. When they run out, Postgres cancels the statement, with the SQLSTATE `55P03` or `57014`.

The implementations of the database raise `UnavailableError` from these timeouts, which are transient (see [Failures of the database](infra.md#failures-of-the-database)).

The API and the consumer create their engines with it. It is a module of its own so that the process of the consumer doesn't load the API, which import-linter checks.

## The consumer

`consumer.py`

`run_consumer(stop, settings=None)` runs the [consumer](consumer.md) until `stop`, an `asyncio.Event`, is set:

1. It reads the settings from the environment variables when `settings` is `None`.
2. It creates the engine of the database with [`database_engine()`](#the-database), and builds a [`UserDeletedHandler`](consumer.md#handling) with `DeleteShortURLsOfUser`, on a `SQLAlchemyUnitOfWork` on that engine.
3. It connects to `RABBITMQ_URL` with `connect_robust()` of aio-pika, and starts consuming with [`consume()`](consumer.md#consuming).
4. When `stop` is set, it closes the connection, and returns. RabbitMQ puts a message that wasn't acknowledged by then back in the queue, so it is handled again.

It disposes the engine when it returns or raises. It raises `SettingsError` for the environment variables, and the `AMQPConnectionError` of aio-pika when RabbitMQ can't be reached when it starts. After that, a lost connection doesn't raise: aio-pika connects again, every 5 seconds, until it succeeds, and the consumer goes on.

`main()` runs `run_consumer()` until the process gets `SIGINT` or `SIGTERM`, which set `stop`, and logs at the level `INFO`, to the standard error, with the default format of `logging`.
