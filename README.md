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

- authentication, sign-up or user management;
- refresh tokens, plans, emails, templates or translations.

### Owner

Every short URL has an owner: there are no anonymous short URLs. The owner is only a reference. The service knows who owns each short URL, but nothing else about the user.

In the upper layers, the owner's identity will come from a JWT validated by the service, and user deletions will arrive as external events. The details are in [docs/domain.md](docs/domain.md#owner).

## Principles

In order of priority: simplicity, organization, readability and tests. What each one means in practice, and the conventions for comments, documentation, issues and commits, are in [CONTRIBUTING.md](CONTRIBUTING.md).

## Architecture

```
shortener/
├── domain/      the shortener's rules
├── use_cases/   orchestrates the domain for each operation
├── adapters/    entry points to the service (HTTP API with FastAPI)
├── infra/       database, settings and external services
└── shared/      code any layer can use
```

Dependencies point inward, toward the domain. The domain imports nothing from the other layers. Any layer can import `shared/`, which imports nothing from the layers.

## Current state

The restructuring happens layer by layer, from the inside out:

| Layer       | Status                                 |
| ----------- | -------------------------------------- |
| `domain`    | Restructured                           |
| `use_cases` | **Being restructured (current phase)** |
| `adapters`  | Waiting                                |
| `infra`     | Waiting                                |

Problems in the upper layers (bugs, broken tests, code that depends on concepts being removed) are ignored until we reach each of them. The scope of the current phase and how to work in it are in [CONTRIBUTING.md](CONTRIBUTING.md#current-phase-use-cases).

## Development

Requirements: Python 3.12 and [Poetry](https://python-poetry.org/).

```bash
poetry install
poetry run task test_shared
poetry run task test_domain
poetry run task test_use_cases
poetry run pytest tests/test_shared tests/test_domain tests/test_use_cases --cov=shortener/shared --cov=shortener/domain --cov=shortener/use_cases --cov-report=term-missing
```

Before changing anything, read [CONTRIBUTING.md](CONTRIBUTING.md).

## Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md): the current phase, the principles and the conventions for code, tests, comments, documentation, issues and commits. They apply to everyone who changes the project.
- [AGENTS.md](AGENTS.md): what is specific to agents, and which documents they read for each kind of task.
- [docs/domain.md](docs/domain.md): what each part of the domain does, as it is in the code, with its rules and open questions.
- [docs/use_cases.md](docs/use_cases.md): what each use case does, and the abstractions the other layers implement for them, as they are in the code, with their rules and open questions.
- [docs/shared.md](docs/shared.md): what each part of `shared/` does, as it is in the code.
- [docs/issues/](docs/issues/README.md): the issues, until the repository is on GitHub.
