# Contributing

How to work in this repository. These rules belong to the project and apply to every change, whoever makes it, person or agent. [AGENTS.md](AGENTS.md) only adds what is specific to agents.

## How the project is developed

The project is developed mostly by agents. Its maintainer decides what the service does: its features, its contracts with other systems and its rules, as the documents of [docs/service/](docs/service/api.md) describe them. How the code does it, its structure, names, algorithms and tests, is up to whoever implements the change, within the rules of this document, which the [checks](#checks) verify.

- The documents of `docs/service/` are where the maintainer sees the service, without reading the code. A change of what the service does isn't finished until they describe it.
- What only the maintainer can decide is asked, and not decided or deduced: a rule of the service, a contract with its clients, the reason behind a past decision, or a trade-off that the documents don't settle.
- A problem found outside the change is reported, or recorded as an [issue](#issues), and not fixed in the same change.

## Making a change

1. Read the [README](README.md), this document, and the documents of what the change touches: those of `docs/service/` for what the service does, and those of [docs/architecture/](docs/architecture/README.md) for the code. Then read the [open issues](#issues) of the area.
2. Change the code, its tests and its documents together.
3. Run `poetry run task check` until it passes.
4. Commit, following [Commits](#commits).

## Checks

`poetry run task check` runs every check, and the CI, in [.github/workflows/ci.yml](.github/workflows/ci.yml), runs the same on every push to `main` and every pull request. A change is finished when it passes.

| Task                        | Checks                                                                                                              |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `poetry run task lint`      | The formatting, and the rules of the linter, with ruff                                                              |
| `poetry run task typecheck` | The type hints, with mypy: strict in `shortener/` and `alembic/`                                                    |
| `poetry run task imports`   | The dependencies between the layers, and between the tests of each layer, with import-linter                        |
| `poetry run task test`      | Every test, with 100% of the lines and branches of `shortener/` covered. It needs Docker, for Postgres and RabbitMQ |

- `poetry run task format` formats the code, and applies the fixes ruff is sure of. `poetry run task test_<layer>`, such as `test_domain`, runs the tests of one layer.
- The settings of each tool are in `pyproject.toml`, with the reason for each choice that isn't obvious. They can change, as anything else, when a need doesn't fit them.
- A finding is fixed in the code. A line that breaks a rule on purpose, such as a test that passes a value of the wrong type to check what the code does with it, says so with a `# noqa` or a `# type: ignore` that names the code of the rule, and a comment when the line doesn't show why.
- The coverage leaves out only what never runs in the tests, such as the bodies of the methods of a `Protocol`, by the settings of coverage, and not by pragmas in the code. Code that the tests can't reach is code to simplify, or to test in another way, such as running a process.
- A warning fails the test that raises it, such as a coroutine that is never awaited.

## Principles

They are in order of priority. When two of them pull in opposite directions, the first one wins.

### Simplicity

Simple code, simple features, simple architecture.

- Solve today's problem with the simplest solution that works. Don't build for hypothetical needs.
- Only create an abstraction (base class, interface, layer of indirection) when there is more than one real use, or when it marks the boundary between layers, like a repository.
- Before adding, consider removing. Code that doesn't serve the shortener goes away.
- Don't add dependencies without a clear need.

### Changeability

Nothing written before is fixed. The code, its names, its abstractions, its tests and its documents change when a new need doesn't fit them.

- When the code doesn't do what a change needs, change it, instead of working around it. If a function can't do what the change needs, change the function, its callers and its tests, rather than add a special case beside it. For example, when the OpenAPI schema had to document the headers of the responses, `SuccessResponse` gained `header_descriptions`, instead of the schema being patched after FastAPI built it.
- New code is easy to extend where its next need is likely. Before finishing it, ask what it would cost if it had to grow tomorrow, and choose the shape that lets it grow without building the growth, which simplicity forbids: a value received instead of a constant, a table instead of a chain of conditions, one place to add a case. For example, an endpoint declares how it answers in a `SuccessResponse`, so a new kind of response is a new class, and no endpoint changes.
- Tests of behavior make it safe: they check what the code does, not how, so they keep passing when the how changes, and fail when the what does.
- Change what the task needs, and no more. Improving code the task doesn't need is another task.

### Organization

Every responsibility in its proper place.

- Each layer has a role (see [Architecture](docs/architecture/README.md)) and dependencies point inward, which import-linter checks. The domain imports nothing from `use_cases`, `api`, `consumer`, `infra`, `bootstrap` or any framework. `shared/` is code any layer can use, and imports nothing from the layers.
- One concept per module, and the module's name says what is inside.
- No repetition: each rule is written in one place and reused.
- Similar structures follow the same shape. Follow the existing pattern before creating a new one, and when a pattern no longer fits, change it everywhere it is used.

### Readability

Whoever reads the code understands what it does without having to decipher it.

- Descriptive, complete names, with no abbreviations. The exception is well-established terms such as `url` and `id`.
- Small functions with a single responsibility. If a name needs an "and", it is probably two functions.
- Explicit code over clever code: straightforward flow, little indirection, no magic.
- Type hints on every function of `shortener/`, which mypy checks.

### Tests

Tests are a priority and follow the same principles: simple, organized, readable and focused.

- Every feature comes with tests covering the happy path, the error cases and the boundaries (for example, a slug's minimum and maximum length).
- One behavior per test. The test's name says which behavior, and in which situation.
- Test behavior, not implementation details.
- Fixing a bug starts with a test that reproduces it.
- Deterministic tests: never rely on the clock, randomness or execution order without controlling them.

How they are written:

- When many tests make the same call with different values, they are one test with a table of `pytest.param`s, each with an `id`. Tests of one attribute each are merged, and repeated setup and asserts are shared, as fixtures and constants.
- A test doesn't check the value of a constant, such as `SLUG_MAX_LENGTH == 30`. An invariant between constants that guarantees a behavior can be checked.
- A test doesn't compare a whole message of an error. It checks what the message has to name, such as a field, a type or a value, with `assert_mentions()`, of `tests/utils/text_helpers.py`, taking the names from the code, such as `Slug.__name__`, so a reworded message doesn't break it.

How they are organized:

- The structure of `tests/` mirrors that of `shortener/`, in flat directories, with one test file per module, and not a directory per class. `tests/test_docs.py` is apart: it checks the [documents](#documents).
- A layer's test directory whose tests use fixtures has its own `conftest.py`, which loads them (from `tests/fixtures/<layer>/`) only from its own layer and the layers below it. `shared/` counts as below every layer, `api`, `consumer` and `infra` aren't below each other, and `bootstrap` is above them all. That way, a broken upper layer never stops a lower layer's tests from running, which import-linter checks. There is no `tests/conftest.py`.
- Each layer is tested on its own, and there are no end-to-end tests for now.

How each layer is tested:

- A use case is tested with doubles of the abstractions it receives, from `tests/fixtures/use_cases/`, and not with fakes that simulate the database. The test sets what each method of a double returns, then checks what the use case returned and the calls it made. Those calls are part of the use case's behavior, not implementation details: what it asks of the other layers, with which arguments and in which order. Check them with `assert_awaited*`, since a coroutine that is called but never awaited does nothing.
- An endpoint is tested in the same way, with doubles of the use cases, from `tests/fixtures/api/`, and not with the real use cases. The test sets what `execute()` of a double returns, then checks the response and the arguments the endpoint gave to `execute()`.
- The handler of the consumer is tested in the same way, with doubles of the use cases and of the messages, from `tests/fixtures/consumer/`. What the consumer declares and consumes is tested against RabbitMQ in a container.
- An implementation in `infra` is tested on its own, against what it implements with: the ones of the database against Postgres in a container, with the migrations applied, and not against SQLite or doubles of the database.
- The assembly of `bootstrap` is tested against Postgres and RabbitMQ in containers, and a process, such as the consumer, as a process.

## Comments

The code should say what it does on its own. Comments are for what it can't say: the reason behind a decision, a nuance, a constraint that comes from outside.

- Don't comment the obvious. If a comment explains *what* the code does, improve the code (names, extracting a function) instead of commenting it.
- Docstrings follow the same rule: they only exist when they add something the name and signature don't say, such as the exceptions that may be raised.
- If an explanation is too long for a comment, write it in a document and leave a short comment in the code pointing there:

  ```python
  # The owner may no longer exist. See docs/architecture/domain.md#owner
  ```

## Documents

The documents are a reflection of the project: what they say is what the code does now, not what it should do. Each one has a subject, and says only what is about it:

- [README](README.md): what the service is, its status, its scope, its architecture in short, and how to start.
- This document: how to work in the project.
- [AGENTS.md](AGENTS.md): what is specific to agents.
- [docs/service/](docs/service/api.md): what the service does, seen from outside, by whoever calls it, runs it or decides what it does: its [API](docs/service/api.md), its [events](docs/service/events.md), its [configuration](docs/service/configuration.md) and [how it runs](docs/service/running.md), with their rules, guarantees and known limitations. They name no module, class or function.
- [docs/service/openapi.yaml](docs/service/openapi.yaml): the exact schema of the API, which `poetry run task openapi` writes from the code, and a test checks.
- [docs/architecture/](docs/architecture/README.md): how the code does it: the layers, and one document per layer, with what each module, class and function does.

### No repetition

Each thing is explained once, in the document whose subject it is, and the others link to it. A fact can appear in a document of the service and in one of the architecture, each at its level, such as the length of a slug, which `docs/service/api.md` gives as a rule for the clients, and `docs/architecture/domain.md` as the constants and the code that check it. But its explanation, its reasons and its edge cases are written once, and the other document links to them. A repeated text is one more to keep up to date, and the first to go stale.

The same goes for the rules of the project: they are written here, and the other documents point to them, instead of repeating them.

### What a document says

A document says two kinds of things, and they are treated differently:

- **What the code does** is concrete, and is either right or wrong. In the documents of the architecture: what each module, class, function and method does, what it receives and returns, which errors it raises and when, and its edge cases, precisely enough to leave no room for interpretation. Private helpers (`_name`) are covered by the description of the code that uses them. In the documents of the service: what a client sends and gets, and what the service guarantees, with no detail of the code. A description that doesn't match the code is fixed, and a missing one is added.
- **Why the code is the way it is** depends on whoever made the decision. Write a why only when it comes from that person: the decision was made in the current task, or its author stated it. Never deduce one from the code. A why that is already written can be judged: if the code contradicts it or it no longer applies, point it out.

A bug that is known but not fixed yet, and a question still open, are [issues](#issues), linked from where a document describes what they affect. When a document grows too large, it becomes a directory with one file per concept (for example, `docs/architecture/domain/shorturl.md`).

### Every change covers its documents

Every task that changes code (a feature, a fix, a refactor, a removal) also covers the documents of what it touches:

1. Before changing the code, read the parts of the documents that describe it.
2. After changing it, fix what became wrong and describe what was added or removed: in `docs/service/` when what the service does changed, and in `docs/architecture/` when the code did.
3. Add the why of a decision made in the task when it helps a later reader understand something the code doesn't show. Weigh it: most changes don't need one.

`tests/test_docs.py` checks that every link between the documents, and every reference of the code to a document, such as the comment above, leads to a file and a heading that exist.

## Issues

The known problems and the open questions are the [issues of GitHub](https://github.com/rafaelblt/shortener/issues). Open one for:

- A problem found during a change, but outside it, to be analyzed and fixed apart.
- A problem complex enough to need investigating before it is fixed.
- A problem or a question that can wait, because it has little impact for now.

An issue describes what was observed: what happens, how to reproduce it, and where in the code. It states the expected behavior only when something already defines it, such as the documentation, and otherwise says that it is still to be decided. What comes later, such as a decision or a part of the fix, is a comment.

- **Labels:** one type, `bug`, `enhancement`, `refactor`, `documentation` or `question`, and the layers involved, such as `domain` or `api`. The open issues of a layer are `gh issue list --label domain`.
- **Closing:** the commit that fixes an issue closes it, with `Closes #17.` in its body. An issue closed without a fix, such as one whose code was rewritten for another reason, says why in its last comment, and is closed as not planned.

Issues #1 to #32 were kept as files in `docs/issues/` until the repository was on GitHub, and were moved with their numbers, so an older commit that names issue 0017 refers to #17.

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

| Type       | Use                                                          |
| ---------- | ------------------------------------------------------------ |
| `feat`     | New feature                                                  |
| `fix`      | Bug fix                                                      |
| `refactor` | Code change that doesn't change behavior, including removals |
| `test`     | Adds or changes tests                                        |
| `docs`     | Documentation                                                |
| `style`    | Formatting and imports, with no logic change                 |
| `chore`    | Configuration, dependencies, tasks and the CI                |

| Scope                           | For                                        |
| ------------------------------- | ------------------------------------------ |
| `domain`, `domain:shorturl`     | Domain                                     |
| `shared`                        | Code any layer can use                     |
| `use_cases`                     | Use cases                                  |
| `api`                           | HTTP API                                   |
| `consumer`                      | Consumer of the events of RabbitMQ         |
| `infra`, `infra:db`             | Infrastructure, and its database           |
| `bootstrap`                     | Settings and the assembly of the processes |
| `fixtures`, `utils`, `conftest` | Test infrastructure (with `test`)          |

Examples from the history:

```
feat(api): answer the Location of the new short URL when creating one
fix(domain): reject target URLs with characters that aren't printable or spaces
refactor(bootstrap): keep the settings of the database in a DatabaseSettings
test(infra:db): check that add raises for an id that is already stored
docs: say how to roll back a version
chore: run the tests, check the lock file and build the image in a CI
```
