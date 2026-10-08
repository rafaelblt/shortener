# AGENTS.md

What is specific to agents working in this repository. The project's rules aren't here: they are in the documents below, and they apply to everyone who changes the project, people and agents alike.

## Before a task

Read the [README](README.md) for the scope, the architecture and the current state, and [CONTRIBUTING.md](CONTRIBUTING.md) for how to work in the project. Then read the documents of what the task touches:

| When the task                                         | Read                                                     |
| ----------------------------------------------------- | -------------------------------------------------------- |
| changes code, tests or documentation                  | [CONTRIBUTING.md](CONTRIBUTING.md), all of it            |
| touches `shortener/domain/` or `tests/test_domain/`   | [docs/domain.md](docs/domain.md)                         |
| opens, closes or adds to an issue                     | [docs/issues/README.md](docs/issues/README.md)           |
| makes a commit                                        | [Commits](CONTRIBUTING.md#commits) in CONTRIBUTING.md    |

## During a task

- Stay inside the task and the [current phase](CONTRIBUTING.md#current-phase-domain). Report the problems you find outside them instead of fixing them.
- When you point out that something breaks a rule, cite the document where the rule is written, not this file. For example: "this repeats a rule, see [Organization](CONTRIBUTING.md#2-organization)".
- Ask the user whatever only they can decide, such as a domain rule or the reason behind a decision, instead of deciding or deducing it.
- Before saying a task is done, run the verification of the current phase and report its result.
- Commit or push only with the user's permission.
