# AGENTS.md

Guide for anyone working in this repository, person or agent. Read it before changing anything.

## Background

Shortener is the back end of a URL shortener. The project grew beyond that (users, authentication, plans, emails, translations), stalled, and is now being restructured to be **only a URL shortener**.

The existing code has flaws: bugs, fragile or missing tests, and concepts outside the scope. It will be rebuilt layer by layer, from the inside out, starting with the domain.

The [README](README.md) explains the service's scope and the owner concept.

## Current phase: domain

The scope is `shortener/domain/` and its tests: `tests/test_domain/` and the fixtures those tests use. Update this section when the phase changes.

- Don't fix `use_cases`, `adapters` or `infra`. Problems in those layers are ignored until we reach them.
- Changes to the domain will break the upper layers. That is expected: don't patch them to keep up.
- This phase is verified with `poetry run task test_domain`. The full suite is not a criterion.
- [docs/domain.md](docs/domain.md) describes the domain as it is in the code, with its rules and open questions. Its known bugs are open issues labeled `domain`, and fixing them is part of this phase. It has to stay faithful to `shortener/domain/` (see [`docs/`](#docs)). If a rule is unclear, ask instead of making one up.

## Principles

They are in order of priority. When two of them pull in opposite directions, the first one wins.

### 1. Simplicity

Simple code, simple features, simple architecture.

- Solve today's problem with the simplest solution that works. Don't build for hypothetical needs.
- Only create an abstraction (base class, interface, layer of indirection) when there is more than one real use, or when it marks the boundary between layers, like a repository.
- Before adding, consider removing. Code that doesn't serve the shortener goes away.
- Don't add dependencies without a clear need.

### 2. Organization

Every responsibility in its proper place.

- Each layer has a role (see the [Architecture](README.md#architecture) in the README) and dependencies point inward. The domain imports nothing from `use_cases`, `adapters`, `infra` or any framework.
- One concept per module, and the module's name says what is inside.
- No repetition: each rule is written in one place and reused.
- Similar structures follow the same shape. Follow the existing pattern before creating a new one.

### 3. Readability

Whoever reads the code understands what it does without having to decipher it.

- Descriptive, complete names, with no abbreviations. The exception is well-established terms such as `url` and `id`.
- Small functions with a single responsibility. If a name needs an "and", it is probably two functions.
- Explicit code over clever code: straightforward flow, little indirection, no magic.
- Use type hints.

### 4. Tests

Tests are a priority and follow the same principles: simple, organized, readable and focused.

- Every feature comes with tests covering the happy path, the error cases and the boundaries (for example, a slug's minimum and maximum length).
- One behavior per test. The test's name says which behavior, and in which situation.
- The structure of `tests/` mirrors that of `shortener/`.
- Each layer's test directory has its own `conftest.py`, which loads fixtures (from `tests/fixtures/<layer>/`) only from its own layer and the layers below it. That way, a broken upper layer never stops a lower layer's tests from running. `tests/conftest.py` never imports project code.
- Deterministic tests: never rely on the clock, randomness or execution order without controlling them.
- Test behavior, not implementation details.
- Fixing a bug starts with a test that reproduces it.

## Comments and documentation

The code should say what it does on its own. Comments are for what it can't say: the reason behind a decision, a nuance, a constraint that comes from outside.

- Don't comment the obvious. If a comment explains *what* the code does, improve the code (names, extracting a function) instead of commenting it.
- Docstrings follow the same rule: they only exist when they add something the name and signature don't say, such as the exceptions that may be raised.
- If an explanation is too long for a comment, write it in `docs/` and leave a short comment in the code pointing there:

  ```python
  # The owner may no longer exist. See docs/domain.md#owner
  ```

### `docs/`

Markdown documentation, starting simple. The idea is one file per layer, and for now only the domain is written: [docs/domain.md](docs/domain.md). When a file grows too large, it becomes a directory with one file per concept (for example, `docs/domain/shorturl.md`).

**Each document is faithful to the code of its layer.** `docs/domain.md` describes `shortener/domain/` as it is now, not as it should be. A bug that is known but not fixed yet becomes an [issue](#issues), linked from where the document describes the affected code.

A document says two kinds of things, and they are treated differently:

- **What the code does** is concrete, and is either right or wrong: what each module, class, function and method does, what it receives and returns, which errors it raises and when, and its edge cases. Each one is described, precisely enough to leave no room for interpretation. Private helpers (`_name`) are covered by the description of the code that uses them. A description that doesn't match the code is fixed, and a missing one is added.
- **Why the code is the way it is** depends on whoever made the decision. Write a why only when it comes from that person: the decision was made in the current task, or its author stated it. Never deduce one from the code. A why that is already written can be judged: if the code contradicts it or it no longer applies, point it out.

Every task that changes code (a feature, a fix, a refactor, a removal) also covers the documentation of what it touches:

1. Before changing the code, read the parts of the document that describe it.
2. After changing it, fix what became wrong and describe what was added or removed.
3. Add the why of a decision made in the task when it helps a later reader understand something the code doesn't show. Weigh it: most changes don't need one.

## Issues

Until the repository is on GitHub, issues live in [docs/issues/](docs/issues/README.md), one file per issue. The format, the states and the workflow are described there.

**The content of an issue is never edited, only added to.** Only the state fields (`status`, `resolution` and `labels`) change. Everything else stays as it was written, and a correction goes in a new entry at the end.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

<body>
```

- **Type:** one of those listed below.
- **Scope** (optional): the layer, and optionally the module, separated by `:`. For example, `domain:shorturl`.
- **Description:** imperative mood, starting in lowercase, with no trailing period. Class and function names keep their spelling from the code.
- **Body** (optional): explains the why, or lists the changes as `-` items.
- One commit per logical change. Several small commits are better than one big commit.

| Type       | Use                                               |
| ---------- | ------------------------------------------------- |
| `feat`     | New feature                                       |
| `fix`      | Bug fix                                           |
| `refactor` | Code change that doesn't change behavior, including removals |
| `test`     | Adds or changes tests                             |
| `docs`     | Documentation                                     |
| `style`    | Formatting and imports, with no logic change      |
| `chore`    | Configuration, dependencies and tasks             |

| Scope                                          | For                                 |
| ---------------------------------------------- | ----------------------------------- |
| `domain`, `domain:shorturl`, `domain:shared`   | Domain                              |
| `use_cases`                                    | Use cases                           |
| `adapters:api`                                 | HTTP API                            |
| `infra:db`, `infra:settings`, `infra:services` | Infrastructure                      |
| `fixtures`, `utils`, `conftest`                | Test infrastructure (with `test`)   |
| `issues`                                       | Issue files (with `docs`)           |

Examples from the history:

```
feat(domain:shared): add __eq__ and __repr__ to PrimaryKey
fix(infra:services): add try except in verify method of PasslibPasswordHasher
refactor(infra:db): remove SQLAlchemyRefreshTokenRepository
test(fixtures): remove refresh token fixtures and repository
chore(tasks): update i18n tasks
```

## Commands

```bash
poetry install
poetry run task test_domain
poetry run pytest tests/test_domain --cov=shortener/domain --cov-report=term-missing
```
