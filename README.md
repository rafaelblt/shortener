# Shortener

Back end of a URL shortener, exposed through an HTTP API.

## Background

The project started as a URL shortener and, over time, piled up responsibilities: user sign-up and login, refresh tokens, plans, emails, templates and translations. That pulled it away from its goal and eventually stalled its development.

It was then rebuilt, layer by layer, from the inside out, around the original idea: **a URL shortener, and nothing else**. Every layer has been rebuilt. What is known to be wrong or missing is in the [open issues](docs/issues/README.md#listing).

## Scope

The service:

- creates, reads, lists, updates and deletes short URLs;
- resolves a slug to its target URL;
- deletes the short URLs of a user when it receives the event of the deletion of the user.

The service does **not** handle:

- issuing access tokens, sign-up or user management;
- refresh tokens, plans, emails, templates or translations.

### Owner

Every short URL has an owner: there are no anonymous short URLs. The owner is only a reference. The service knows who owns each short URL, but nothing else about the user.

The owner's identity comes from an access token, a JWT issued outside the service, which the service only validates, and user deletions arrive as events, published to RabbitMQ by the system responsible for the identities of the users. The details are in [Owner](docs/architecture/domain.md#owner), [Access tokens](docs/service/api.md#access-tokens) and [Events](docs/service/events.md).

## How it fits

```
systems that use the shortener ── HTTP ──▶ API ─────────┐
                                                        ├──▶ Postgres
the system of the identities ─ RabbitMQ ─▶ consumer ────┘
of the users
```

The service is two processes, from the same image: the API, which answers the requests of the systems that use the shortener, and the consumer, which handles the events. Both use the same Postgres database. The system of the identities of the users issues the access tokens the API verifies, and publishes the deletions of the users the consumer handles. How the processes run is in [Running](docs/service/running.md).

## Architecture

```
shortener/
├── domain/      the rules of the short URLs
├── use_cases/   orchestrates the domain for each operation
├── api/         an entry point: the HTTP API, with FastAPI
├── consumer/    the other entry point: the events of RabbitMQ, with aio-pika
├── infra/       implements what the other layers need from outside: database, clock, access tokens,
│                rate limit
├── bootstrap/   reads the settings, and assembles the layers into the two processes
└── shared/      code any layer can use
```

Dependencies point inward, toward the domain, and a check fails when they don't. The details are in [docs/architecture/](docs/architecture/README.md).

## Development

Requirements: Python 3.12, [Poetry](https://python-poetry.org/), and Docker, which the tests use to run Postgres and RabbitMQ.

```bash
poetry install
poetry run task check
```

`poetry run task check` runs the formatter, the linter, the type checker, the checks of the architecture and the tests, as the CI does. Before changing anything, read [CONTRIBUTING.md](CONTRIBUTING.md).

### Running with Docker Compose

To try the service locally without setting anything, [compose.yaml](compose.yaml) runs the API and the consumer with Postgres, RabbitMQ, the migrations applied and settings that are only good for local tests:

```bash
docker compose up --build
```

The API answers at `http://localhost:8000`, as [its documentation](docs/service/api.md) describes, and the management page of RabbitMQ, which shows its queues, at `http://localhost:15672`, with the user `shortener` and the password `shortener`. The data of the database and of RabbitMQ stays in the volumes `db` and `rabbitmq` until `docker compose down -v`.

The service doesn't issue access tokens, so the `token` service issues one the API accepts, valid for a day, for the user of the UUID it receives, or for `00000000-0000-4000-8000-000000000001` without one:

```bash
TOKEN=$(docker compose run --rm -q token)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/v1/shorturls
```

The issuer of the events doesn't exist yet either, so the `user-deleted` service publishes the [event](docs/service/events.md#the-message) of the deletion of the user of the UUID it receives, or of `00000000-0000-4000-8000-000000000001` without one, and the consumer deletes the short URLs of that user:

```bash
docker compose run --rm -q user-deleted
```

To run the service in another way, its settings are in [Configuration](docs/service/configuration.md), and its processes in [Running](docs/service/running.md).

## Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md): how to work in the project, person or agent: the principles, the checks, and the conventions of the tests, comments, documents, issues and commits.
- [AGENTS.md](AGENTS.md): what is specific to agents.
- [docs/service/](docs/service/api.md): what the service does, seen from outside: its [API](docs/service/api.md), with its [OpenAPI schema](docs/service/openapi.yaml), its [events](docs/service/events.md), its [configuration](docs/service/configuration.md) and [how it runs](docs/service/running.md).
- [docs/architecture/](docs/architecture/README.md): how the code does it: the layers, and one document per layer.
- [docs/issues/](docs/issues/README.md): the issues, until the repository is on GitHub.
