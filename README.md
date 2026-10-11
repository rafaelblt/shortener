# Shortener

Back end of a URL shortener, exposed through an HTTP API.

> **Under restructuring.** The current code has flaws (bugs, fragile or missing tests, concepts that don't belong in a URL shortener) and is being rebuilt layer by layer, starting with the domain. See [Current state](#current-state).

## Background

The project started as a URL shortener and, over time, piled up responsibilities: user sign-up and login, refresh tokens, plans, emails, templates and translations. That pulled it away from its goal and eventually stalled its development.

The restructuring goes back to the original idea: **a URL shortener, and nothing else**.

## Scope

The service:

- creates, reads, lists, updates and deletes short URLs;
- resolves a slug to its target URL.

The service does **not** handle:

- issuing access tokens, sign-up or user management;
- refresh tokens, plans, emails, templates or translations.

### Owner

Every short URL has an owner: there are no anonymous short URLs. The owner is only a reference. The service knows who owns each short URL, but nothing else about the user.

The owner's identity comes from an access token, a JWT issued outside the service, which the service only validates, and user deletions will arrive as external events. The details are in [docs/domain.md](docs/domain.md#owner) and [docs/api.md](docs/api.md#authentication).

## Principles

In order of priority: simplicity, organization, readability and tests. What each one means in practice, and the conventions for comments, documentation, issues and commits, are in [CONTRIBUTING.md](CONTRIBUTING.md).

## Architecture

```
shortener/
├── domain/      the shortener's rules
├── use_cases/   orchestrates the domain for each operation
├── api/         the entry point to the service: the HTTP API, with FastAPI
├── infra/       implements the abstractions of the other layers: database, clock, access tokens
├── bootstrap/   the settings, and the assembly of the layers into the application
└── shared/      code any layer can use
```

Dependencies point inward, toward the domain. The domain imports nothing from the other layers. `api` and `infra` import the inner layers, and not each other: `bootstrap` is the only layer that imports both, to assemble them. Any layer can import `shared/`, which imports nothing from the layers.

## Current state

The restructuring happens layer by layer, from the inside out, and the outer layers are rebuilt together:

| Layer       | Status                                 |
| ----------- | -------------------------------------- |
| `domain`    | Restructured                           |
| `use_cases` | Restructured                           |
| `api`       | **Being restructured (current phase)** |
| `infra`     | **Being restructured (current phase)** |
| `bootstrap` | **Being restructured (current phase)** |

The scope of the current phase and how to work in it are in [CONTRIBUTING.md](CONTRIBUTING.md#current-phase-outer-layers).

## Development

Requirements: Python 3.12, [Poetry](https://python-poetry.org/), and Docker, which the tests of `infra` use to run Postgres.

```bash
poetry install
poetry run task test_layers
poetry run pytest --cov=shortener --cov-report=term-missing
```

Before changing anything, read [CONTRIBUTING.md](CONTRIBUTING.md).

## Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md): the current phase, the principles and the conventions for code, tests, comments, documentation, issues and commits. They apply to everyone who changes the project.
- [AGENTS.md](AGENTS.md): what is specific to agents, and which documents they read for each kind of task.
- [docs/domain.md](docs/domain.md): what each part of the domain does, as it is in the code, with its rules and open questions.
- [docs/use_cases.md](docs/use_cases.md): what each use case does, and the abstractions the other layers implement for them, as they are in the code, with their rules and open questions.
- [docs/api.md](docs/api.md): how the API turns the use cases into endpoints, its endpoints, errors and authentication, as they are in the code, with their rules and open questions.
- [docs/infra.md](docs/infra.md): the implementations of the abstractions, as they are in the code, with their rules and open questions.
- [docs/bootstrap.md](docs/bootstrap.md): the settings, and how the application is assembled and run, as they are in the code.
- [docs/shared.md](docs/shared.md): what each part of `shared/` does, as it is in the code.
- [docs/issues/](docs/issues/README.md): the issues, until the repository is on GitHub.
