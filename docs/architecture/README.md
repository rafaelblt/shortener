# Architecture

How the code is organized, and where each thing is. What the service does, seen from outside, is in [docs/service/](../service/api.md), and each of the other documents of this directory describes the code of one layer, as it is now: each module, class and function, what it receives and returns, the errors it raises, and its edge cases.

## Layers

```
shortener/
├── domain/      the rules of the short URLs
├── use_cases/   orchestrates the domain for each operation, and defines what it needs from outside
├── api/         an entry point: the HTTP API, with FastAPI
├── consumer/    the other entry point: the events of RabbitMQ, with aio-pika
├── infra/       implements what the other layers need from outside: database, clock, access tokens,
│                rate limit
├── bootstrap/   reads the settings, and assembles the layers into the two processes
└── shared/      code any layer can use

alembic/         the migrations of the database
```

| Layer                          | Document                     |
| ------------------------------ | ---------------------------- |
| `shortener/domain/`            | [domain.md](domain.md)       |
| `shortener/use_cases/`         | [use_cases.md](use_cases.md) |
| `shortener/api/`               | [api.md](api.md)             |
| `shortener/consumer/`          | [consumer.md](consumer.md)   |
| `shortener/infra/`, `alembic/` | [infra.md](infra.md)         |
| `shortener/bootstrap/`         | [bootstrap.md](bootstrap.md) |
| `shortener/shared/`            | [shared.md](shared.md)       |

## Dependencies

Dependencies point inward, toward the domain:

- The domain imports nothing from the other layers, and no framework.
- The use cases import only the domain, and no framework.
- `api`, `consumer` and `infra` import the inner layers, and not each other. The API and the consumer reach the database and the access tokens only through abstractions, which `infra` implements.
- `bootstrap` is the only layer that imports them all, to assemble them, and the process of the consumer doesn't load the API.
- Any layer can import `shared/`, which imports no layer.

import-linter checks these rules, with the contracts of `pyproject.toml` (see [Checks](../../CONTRIBUTING.md#checks)), and the same ones for the tests of each layer.

What a layer needs from outside, it defines as an abstraction, a `Protocol`, which an outer layer implements without inheriting from it: the use cases define [the repository, the unit of work, the current user and the clock](use_cases.md#abstractions), and the API defines [the verifier of access tokens, the rate limiter, the health check and the factory of use cases](api.md#overview). `bootstrap` builds the implementations, and gives them to the layers that use them.

## A request

How the API answers `POST /api/v1/shorturls`, as every endpoint does:

1. FastAPI parses the JSON of the body, counts the request in the [rate limit](api.md#rate-limit), and reads the values of the request into the parameters of the endpoint, which [`add_route()`](api.md#how-an-endpoint-works) built from the signature of `CreateShortURL.execute()`.
2. The endpoint builds the [current user](api.md#authentication) of the request from its access token, and asks the [factory of use cases](api.md#use-cases), which `bootstrap` implements, for `CreateShortURL`, built with it.
3. [`CreateShortURL`](use_cases.md#createshorturl) asks for the user, checks the values with the [domain](domain.md#value-objects), and adds the [`ShortURL`](domain.md#shorturl) through a transaction of the [unit of work](use_cases.md#unit-of-work), which [`infra`](infra.md#unit-of-work) implements on Postgres.
4. It returns a `Result`: `Ok` with the details of the short URL, which the endpoint answers with its [response](api.md#responses), or `Err` with an error, which the endpoint answers with the [error](api.md#errors) mapped to it.

## An event

How the consumer handles the deletion of a user:

1. RabbitMQ delivers a message of the queue of the service, which [`consume()`](consumer.md#consuming) consumes with the handler.
2. [`UserDeletedHandler`](consumer.md#handling) takes the user from the body, and runs [`DeleteShortURLsOfUser`](use_cases.md#deleteshorturlsofuser), which removes the short URLs of the user through a transaction.
3. It acknowledges the message after the deletion is committed, or rejects it, or puts it back in the queue, by what failed.

## Across the layers

- **Errors are values.** The errors a caller has to handle, such as a slug that is taken, are returned in a [`Result`](shared.md#result), as frozen dataclasses. Exceptions are only for programming errors, and for [`UnavailableError`](use_cases.md#unavailableerror), which the implementations raise for a failure that trying again may fix, and which the API answers with `503`.
- **Time is given.** The domain never reads the clock: it receives `now` (see [Time](domain.md#time)), which the use cases read from the [`Clock`](use_cases.md#clock), which [`infra`](infra.md#clock) implements in UTC.
- **Values are checked at the edge of the domain.** What a client sends is checked against the rules of the domain, with the `create()` of each value object, and what was stored is only parsed, with `parse()`, so a value accepted under older rules keeps working (see [Value objects](domain.md#value-objects)).
