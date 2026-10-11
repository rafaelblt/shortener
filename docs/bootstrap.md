# Bootstrap

`bootstrap` assembles the application: it reads the settings, builds the implementations of [`infra`](infra.md), builds the [use cases](use_cases.md) with them, and gives them to the [API](api.md). It lives in `shortener/bootstrap/`, and is the only layer that imports from every other one.

This document describes `bootstrap` as it is in the code. Verified bugs that aren't fixed yet are [issues](issues/README.md) labeled `bootstrap`, linked from where this document describes the code they affect. Decisions still to be made are in [Open questions](#open-questions).

## Overview

```
shortener/bootstrap/
├── settings.py    Settings, AccessTokenSettings and SettingsError
├── use_cases.py   UseCases
└── app.py         create_app() and access_token_verifier()
```

## Settings

`settings.py`

`Settings.from_environment(environment=os.environ)` reads the settings from the environment variables:

| Variable         | Required        | Value                                                                                                                                                 |
| ---------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DATABASE_URL`   | Yes             | The URL of the Postgres database, with the driver of asyncpg, such as `postgresql+asyncpg://user:password@localhost:5432/shortener`. The [migrations](infra.md#migrations) read it too. |
| `JWT_ALGORITHMS` | Yes             | The algorithms an access token may be signed with, separated by commas, such as `RS256` or `HS256`                                                    |
| `JWT_ISSUER`     | Yes             | The issuer of the tokens, which their `iss` claim has to be                                                                                           |
| `JWT_AUDIENCE`   | Yes             | The audience of the tokens, which their `aud` claim has to be or have                                                                                 |
| `JWT_KEY`        | One of the two  | The key that verifies the tokens: the secret of the HMAC algorithms, or the public key of the others, in PEM                                          |
| `JWT_JWKS_URL`   | One of the two  | The URL where the issuer publishes the keys that verify the tokens, as a JWKS                                                                         |

- A value is stripped of spaces, and an empty one is the same as a variable that isn't set. In `JWT_ALGORITHMS`, an empty item between commas is left out.
- It raises `SettingsError` when the variables don't make valid settings, with a message that names every problem: a required variable that is missing, a `DATABASE_URL` that isn't a URL of `postgresql+asyncpg`, and both or neither of `JWT_KEY` and `JWT_JWKS_URL`.
- Otherwise, it returns a `Settings`, with the `database_url`, and the settings of the access tokens in an `AccessTokenSettings`: `algorithms`, as a tuple, `issuer`, `audience`, and `key` and `jwks_url`, of which exactly one isn't `None`.
- Whether the algorithms and the key can verify tokens is checked when the application is built, by [`JWTAccessTokenVerifier`](infra.md#access-tokens).
- It doesn't read a `.env` file. The variables come from the environment of the process, where uvicorn can load a file with `--env-file`.

## Use cases

`use_cases.py`

`UseCases(uow, shorturls, clock)` implements the [`UseCaseFactory`](api.md#use-cases) of the API. `build(use_case, current_user)` builds a use case with these, and raises `LookupError` for a class that isn't one of them:

| Use case                                                                  | Built with                                   |
| ------------------------------------------------------------------------- | -------------------------------------------- |
| `ResolveSlug`                                                             | `uow` and `clock`                            |
| `CreateShortURL`                                                          | `uow`, `current_user` and `clock`            |
| `GetShortURL` and `ListShortURLs`                                         | `shorturls`, a `ShortURLReader`, and `current_user` |
| `UpdateShortURL`, `EnableShortURL`, `DisableShortURL` and `DeleteShortURL` | `uow` and `current_user`                    |

The API builds the use case of each request, with the user of the request. Building one doesn't connect to anything.

## The application

`app.py`

`create_app(settings=None)` returns the application:

1. It reads the settings from the environment variables when `settings` is `None`.
2. It creates the `AsyncEngine` of SQLAlchemy for `DATABASE_URL`, with the default pool of SQLAlchemy and `pool_pre_ping`: the engine only connects when it is first used, and checks a connection of the pool before using it, so it replaces the ones the server closed, such as after a restart.
3. It builds `UseCases` with `SQLAlchemyUnitOfWork` and `SQLAlchemyShortURLReader`, on that engine, and `UTCClock`.
4. It builds the verifier of access tokens with `access_token_verifier()`.
5. It returns the application of [`create_app()`](api.md#the-application) of the API, with a lifespan that disposes the engine when the application stops.

It raises `SettingsError` for the environment variables, `ValueError` when the settings of the access tokens can't verify tokens, and `LookupError` from the API.

`access_token_verifier(settings)` returns a `JWTAccessTokenVerifier`: `with_jwks()` when `jwks_url` isn't `None`, and `with_key()` otherwise. It raises `SettingsError` when both are `None`, which only settings built in code, and not by `from_environment()`, can be.

## Running

The application runs with uvicorn, which calls `create_app()` as a factory:

```bash
poetry run alembic upgrade head
poetry run uvicorn shortener.bootstrap.app:create_app --factory --host 0.0.0.0 --port 8000
```

`poetry run task run` runs it with `--reload`, for development. Both need the [environment variables](#settings).

## Open questions

Decisions to make during this phase.

- **Database.** The pool of connections, and the time the service waits to connect, for a lock or for a statement, are the defaults of SQLAlchemy, asyncpg and Postgres: no setting changes them. Which ones to set, and whether through environment variables, is still to be decided.
