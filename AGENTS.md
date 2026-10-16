# AGENTS.md

What is specific to agents working in this repository. The project's rules aren't here: they are in [CONTRIBUTING.md](CONTRIBUTING.md), and they apply to everyone who changes the project, people and agents alike.

## Map

| Where                                             | What                                                                                      |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| [README.md](README.md)                            | What the service is, its scope, its architecture in short, and how to start               |
| [CONTRIBUTING.md](CONTRIBUTING.md)                | How to work: the principles, the checks, the tests, the documents, the issues and commits |
| [docs/service/](docs/service/api.md)              | What the service does, seen from outside: its API, events, configuration and how it runs  |
| [docs/architecture/](docs/architecture/README.md) | How the code does it: the layers, and one document per layer                              |
| [docs/issues/](docs/issues/README.md)             | The known problems and the open questions                                                 |
| `pyproject.toml`                                  | The dependencies, the tasks, and the settings of the checks                               |

## Before a task

Read [CONTRIBUTING.md](CONTRIBUTING.md), all of it, and [docs/architecture/README.md](docs/architecture/README.md). Then read the documents of what the task touches:

| When the task                                                   | Read                                                             |
| --------------------------------------------------------------- | ---------------------------------------------------------------- |
| changes what the API receives or answers                        | [docs/service/api.md](docs/service/api.md)                       |
| changes the events the service receives, or how it handles them | [docs/service/events.md](docs/service/events.md)                 |
| adds or changes a setting                                       | [docs/service/configuration.md](docs/service/configuration.md)   |
| changes how the processes run                                   | [docs/service/running.md](docs/service/running.md)               |
| touches `shortener/domain/` or `tests/test_domain/`             | [docs/architecture/domain.md](docs/architecture/domain.md)       |
| touches `shortener/use_cases/` or `tests/test_use_cases/`       | [docs/architecture/use_cases.md](docs/architecture/use_cases.md) |
| touches `shortener/api/` or `tests/test_api/`                   | [docs/architecture/api.md](docs/architecture/api.md)             |
| touches `shortener/consumer/` or `tests/test_consumer/`         | [docs/architecture/consumer.md](docs/architecture/consumer.md)   |
| touches `shortener/infra/`, `alembic/` or `tests/test_infra/`   | [docs/architecture/infra.md](docs/architecture/infra.md)         |
| touches `shortener/bootstrap/` or `tests/test_bootstrap/`       | [docs/architecture/bootstrap.md](docs/architecture/bootstrap.md) |
| touches `shortener/shared/` or `tests/test_shared/`             | [docs/architecture/shared.md](docs/architecture/shared.md)       |
| opens, closes or adds to an issue                               | [docs/issues/README.md](docs/issues/README.md)                   |
| makes a commit                                                  | [Commits](CONTRIBUTING.md#commits) in CONTRIBUTING.md            |

## During a task

- Stay inside the task. Report the problems you find outside it instead of fixing them.
- When you point out that something breaks a rule, cite the document where the rule is written, not this file. For example: "this repeats an explanation, see [No repetition](CONTRIBUTING.md#no-repetition)".
- Ask the user whatever only they can decide (see [How the project is developed](CONTRIBUTING.md#how-the-project-is-developed)), instead of deciding or deducing it.
- Before saying a task is done, run `poetry run task check` and report its result.
- Commit or push only with the user's permission.
