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

In order of priority:

1. **Simplicity.** Simple code, simple features, simple architecture.
2. **Organization.** Every responsibility in its proper place, with no repetition.
3. **Readability.** Anyone understands the code by reading it: no excessive abstraction, abbreviations or long functions.
4. **Tests.** Every feature well covered, by tests that follow the principles above.

The practical rules for each principle, for comments, documentation and commits are in [AGENTS.md](AGENTS.md).

## Architecture

```
shortener/
├── domain/      the shortener's rules
├── use_cases/   orchestrates the domain for each operation
├── adapters/    entry points to the service (HTTP API with FastAPI)
└── infra/       database, settings and external services
```

Dependencies point inward, toward the domain. The domain imports nothing from the other layers.

## Current state

The restructuring happens layer by layer, from the inside out:

| Layer       | Status                                 |
| ----------- | -------------------------------------- |
| `domain`    | **Being restructured (current phase)** |
| `use_cases` | Waiting                                |
| `adapters`  | Waiting                                |
| `infra`     | Waiting                                |

**The scope of this phase is the domain and its tests.** Problems in the upper layers (bugs, broken tests, code that depends on concepts being removed) are ignored until we reach each of them. That includes the breakage caused by cleaning up the domain itself.

## Development

Requirements: Python 3.12 and [Poetry](https://python-poetry.org/).

```bash
poetry install
poetry run task test_domain
poetry run pytest tests/test_domain --cov=shortener/domain --cov-report=term-missing
```

## Documentation

- [AGENTS.md](AGENTS.md): principles and conventions for code, tests, comments, documentation, issues and commits.
- [docs/domain.md](docs/domain.md): what each part of the domain does, as it is in the code, with its rules and open questions.
- [docs/issues/](docs/issues/README.md): the issues, until the repository is on GitHub.
